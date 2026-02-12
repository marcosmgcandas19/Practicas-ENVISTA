from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CinenvistaTicketWizard(models.TransientModel):
    _name = 'cinenvista.ticket.wizard'
    _description = 'Asistente de Venta Rápida de Entradas'


    screening_id = fields.Many2one('cinenvista.screening', string='Sesión', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    qty_regular = fields.Integer(string='Entradas regulares', default=0)
    qty_vip = fields.Integer(string='Entradas VIP', default=0)
    redeem_points = fields.Boolean(string='¿Canjear puntos por entrada gratis?')


    room_id = fields.Many2one(
        related='screening_id.room_id',
        string='Sala',
        store=False
    )
   
    occupied_seat_ids = fields.Many2many(
        'cinenvista.seat',
        compute='_compute_occupied_seats',
        string='Butacas Ocupadas'
    )
   
    selected_seat_ids = fields.Many2many(
        'cinenvista.seat',
        string='Seleccionar Butacas',
        domain="[('room_id', '=', room_id), ('id', 'not in', occupied_seat_ids)]"
    )


    @api.depends('screening_id')
    def _compute_occupied_seats(self):
        """Busca butacas ya reservadas en sesiones confirmadas"""
        for wizard in self:
            if wizard.screening_id:
                reservations = self.env['cinenvista.reservation'].search([
                    ('screening_id', '=', wizard.screening_id.id),
                    ('state', '=', 'confirmed')
                ])
                wizard.occupied_seat_ids = reservations.mapped('seat_ids')
            else:
                wizard.occupied_seat_ids = self.env['cinenvista.seat']


    def action_confirm_sale(self):
        self.ensure_one()
       
        # 1. VALIDACIONES DE BUTACAS
        if not self.selected_seat_ids:
            raise ValidationError(_("Debe seleccionar al menos una butaca específica."))
       
        total_requested = len(self.selected_seat_ids)
        total_input_qty = self.qty_regular + self.qty_vip
       
        if total_input_qty != total_requested:
             raise ValidationError(_("La suma de entradas (%s) no coincide con las butacas seleccionadas (%s).") % (total_input_qty, total_requested))


        # 2. LÓGICA DE PUNTOS
        points_to_deduct = 0
        free_regular = False
        free_vip = False


        if self.redeem_points:
            # Prioridad VIP (200 pts) o Regular (100 pts)
            if self.qty_vip > 0 and self.partner_id.loyalty_points >= 200:
                free_vip = True
                points_to_deduct = 200
            elif self.qty_regular > 0 and self.partner_id.loyalty_points >= 100:
                free_regular = True
                points_to_deduct = 100
            else:
                raise ValidationError(_("No tienes puntos suficientes para el canje solicitado."))


        # 3. ACTUALIZACIÓN DE MOTOR DE PUNTOS Y NIVEL
        points_earned = total_requested * 10
        new_total_points = (self.partner_id.loyalty_points + points_earned) - points_to_deduct
       
        new_level = 'standard'
        if new_total_points > 1000:
            new_level = 'premium'
        elif new_total_points > 500:
            new_level = 'silver'
       
        self.partner_id.write({
            'loyalty_points': new_total_points,
            'member_level': new_level
        })


        # 4. CÁLCULO DE DESCUENTO POR NIVEL
        discount = 0.0
        if self.partner_id.member_level == 'silver':
            discount = 10.0
        elif self.partner_id.member_level == 'premium':
            discount = 20.0


        # 5. CREACIÓN DEL PEDIDO DE VENTA (SALE ORDER)
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })


        order_lines = []
        #  Regular
        if self.qty_regular > 0:
            vals = {
                'product_id': self.env.ref('cinenvista.product_ticket_regular').id,
                'product_uom_qty': self.qty_regular,
            }
            if free_regular:
                vals['price_unit'] = 0.0
            else:
                vals['discount'] = discount
            order_lines.append((0, 0, vals))


        #  VIP
        if self.qty_vip > 0:
            vals = {
                'product_id': self.env.ref('cinenvista.product_ticket_vip').id,
                'product_uom_qty': self.qty_vip,
            }
            if free_vip:
                vals['price_unit'] = 0.0
            else:
                vals['discount'] = discount
            order_lines.append((0, 0, vals))


        sale_order.write({'order_line': order_lines})
        sale_order.action_confirm()


        # 6. CREACIÓN DE LA RESERVA VINCULADA
        self.env['cinenvista.reservation'].create({
            'screening_id': self.screening_id.id,
            'partner_id': self.partner_id.id,
            'qty_regular': self.qty_regular,
            'qty_vip': self.qty_vip,
            'seat_ids': [(6, 0, self.selected_seat_ids.ids)],
            'state': 'confirmed',
            'sale_order_id': sale_order.id,
        })


        return {'type': 'ir.actions.act_window_close'}
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CinenvistaTicketWizard(models.TransientModel):
    _name = 'cinenvista.ticket.wizard'
    _description = 'Asistente de Venta Rápida de Entradas'

    screening_id = fields.Many2one('cinenvista.screening', string='Sesión', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    
    # Campos de cantidad 
    qty_regular = fields.Integer(string='Entradas regulares', default=0)
    qty_vip = fields.Integer(string='Entradas VIP', default=0)

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
        for wizard in self:
            if wizard.screening_id:
                # Buscamos todas las reservas confirmadas para esta sesión
                reservations = self.env['cinenvista.reservation'].search([
                    ('screening_id', '=', wizard.screening_id.id),
                    ('state', '=', 'confirmed')
                ])
                # Extraemos los IDs de las butacas 
                wizard.occupied_seat_ids = reservations.mapped('seat_ids')
            else:
                wizard.occupied_seat_ids = self.env['cinenvista.seat']

    def action_confirm_sale(self):
        self.ensure_one()
        
        # 1. Validaciones
        if not self.selected_seat_ids:
            raise ValidationError(_("Debe seleccionar al menos una butaca específica."))
        
        total_requested = len(self.selected_seat_ids)
        total_input_qty = self.qty_regular + self.qty_vip
        
        # Validar que las cantidades coincidan con las butacas seleccionadas
        if total_input_qty != total_requested:
             raise ValidationError(_("La suma de entradas (%s) no coincide con las butacas seleccionadas (%s).") % (total_input_qty, total_requested))

        # 2. Crear pedido de venta 
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'order_line': [],
        })

        # 3. Añadir líneas de pedido
        order_lines = []
        if self.qty_regular > 0:
            product_reg = self.env.ref('cinenvista.product_ticket_regular')
            order_lines.append((0, 0, {
                'product_id': product_reg.id,
                'product_uom_qty': self.qty_regular,
            }))

        if self.qty_vip > 0:
            product_vip = self.env.ref('cinenvista.product_ticket_vip')
            order_lines.append((0, 0, {
                'product_id': product_vip.id,
                'product_uom_qty': self.qty_vip,
            }))

        sale_order.write({'order_line': order_lines})
        sale_order.action_confirm()

        # 4. Crear la reserva vinculando las butacas seleccionadas
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
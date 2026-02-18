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
    
    # Campo computado para mostrar puntos disponibles
    available_points = fields.Integer(
        string='Puntos Disponibles',
        related='partner_id.loyalty_points',
        readonly=True
    )


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
        """Validar y delegar a método según si se canjean puntos o no"""
        self.ensure_one()
       
        # VALIDACIONES INICIALES
        if not self.selected_seat_ids:
            raise ValidationError(_("Debe seleccionar al menos una butaca específica."))
       
        total_requested = len(self.selected_seat_ids)
        total_input_qty = self.qty_regular + self.qty_vip
       
        if total_input_qty != total_requested:
            raise ValidationError(
                _("La suma de entradas (%s) no coincide con las butacas seleccionadas (%s).") 
                % (total_input_qty, total_requested)
            )

        # Delegar según si se canjean puntos o no
        if self.redeem_points:
            return self._process_redeem_points()
        else:
            return self._process_normal_sale()

    def _process_redeem_points(self):
        """Procesar venta canjeando TODAS las entradas posibles por puntos"""
        # 1. CALCULAR CUÁNTAS ENTRADAS SE PUEDEN CANJEAR
        available_points = self.partner_id.loyalty_points
        free_vip_qty = 0
        free_regular_qty = 0
        points_to_deduct = 0

        # Prioridad: Primero canjear VIPs (200 pts cada una)
        if self.qty_vip > 0:
            canjeables_vip = min(self.qty_vip, available_points // 200)
            free_vip_qty = canjeables_vip
            points_to_deduct += canjeables_vip * 200
            available_points -= points_to_deduct

        # Luego canjear Regulares (100 pts cada una) con los puntos restantes
        if self.qty_regular > 0 and available_points >= 100:
            canjeables_regular = min(self.qty_regular, available_points // 100)
            free_regular_qty = canjeables_regular
            points_to_deduct += canjeables_regular * 100

        # Si no hay nada que canjear, error
        if points_to_deduct == 0:
            raise ValidationError(_("No tienes suficientes puntos para canjear entradas."))

        # 2. ACTUALIZAR PUNTOS (RESTAR LOS CANJEADOS)
        new_total_points = self.partner_id.loyalty_points - points_to_deduct
        
        new_level = 'standard'
        if new_total_points > 1000:
            new_level = 'premium'
        elif new_total_points > 500:
            new_level = 'silver'
       
        self.partner_id.with_context(loyalty_already_processed=True).write({
            'loyalty_points': new_total_points,
            'member_level': new_level
        })

        # 3. CREAR PEDIDO DE VENTA
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })

        order_lines = []
        
        # Entradas regulares
        if self.qty_regular > 0:
            if free_regular_qty > 0:
                # Entradas gratis por canje
                order_lines.append((0, 0, {
                    'product_id': self.env.ref('cinenvista.product_ticket_regular').id,
                    'product_uom_qty': free_regular_qty,
                    'price_unit': 0.0
                }))
            # Resto a precio normal (entradas no canjeadas)
            if self.qty_regular > free_regular_qty:
                order_lines.append((0, 0, {
                    'product_id': self.env.ref('cinenvista.product_ticket_regular').id,
                    'product_uom_qty': self.qty_regular - free_regular_qty,
                }))

        # Entradas VIP
        if self.qty_vip > 0:
            if free_vip_qty > 0:
                # Entradas gratis por canje
                order_lines.append((0, 0, {
                    'product_id': self.env.ref('cinenvista.product_ticket_vip').id,
                    'product_uom_qty': free_vip_qty,
                    'price_unit': 0.0
                }))
            # Resto a precio normal (entradas no canjeadas)
            if self.qty_vip > free_vip_qty:
                order_lines.append((0, 0, {
                    'product_id': self.env.ref('cinenvista.product_ticket_vip').id,
                    'product_uom_qty': self.qty_vip - free_vip_qty,
                }))

        sale_order.write({'order_line': order_lines})
        sale_order.action_confirm()

        # 4. CREAR RESERVA - sale_order_id previene que se procesen puntos de nuevo
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

    def _process_normal_sale(self):
        """Procesar venta normal (sin canjear puntos, con descuento por nivel)"""
        # 1. CALCULAR PUNTOS A GANAR Y NUEVO NIVEL
        total_requested = len(self.selected_seat_ids)
        points_earned = total_requested * 10
        new_total_points = self.partner_id.loyalty_points + points_earned
        
        new_level = 'standard'
        if new_total_points > 1000:
            new_level = 'premium'
        elif new_total_points > 500:
            new_level = 'silver'
       
        self.partner_id.with_context(loyalty_already_processed=True).write({
            'loyalty_points': new_total_points,
            'member_level': new_level
        })

        # 2. CALCULAR DESCUENTO POR NIVEL
        discount = 0.0
        if new_level == 'silver':
            discount = 10.0
        elif new_level == 'premium':
            discount = 20.0

        # 3. CREAR PEDIDO DE VENTA
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })

        order_lines = []
        
        # Entradas regulares con descuento
        if self.qty_regular > 0:
            order_lines.append((0, 0, {
                'product_id': self.env.ref('cinenvista.product_ticket_regular').id,
                'product_uom_qty': self.qty_regular,
                'discount': discount
            }))

        # Entradas VIP con descuento
        if self.qty_vip > 0:
            order_lines.append((0, 0, {
                'product_id': self.env.ref('cinenvista.product_ticket_vip').id,
                'product_uom_qty': self.qty_vip,
                'discount': discount
            }))

        sale_order.write({'order_line': order_lines})
        sale_order.action_confirm()

        # 4. CREAR RESERVA - sale_order_id previene que se procesen puntos de nuevo
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
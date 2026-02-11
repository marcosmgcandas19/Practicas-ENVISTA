from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CinenvistaReservation(models.Model):
    _name = 'cinenvista.reservation'
    _description = 'Reservas'

    name = fields.Char(
        string='Código de Ticket', 
        default='New',
        copy=False, 
        readonly=True
    )
    partner_id = fields.Many2one('res.partner', string='Cliente')
    screening_id = fields.Many2one('cinenvista.screening', string='Sesión', required=True)
    qty_regular = fields.Integer(string='Entradas regulares', default=0)
    qty_vip = fields.Integer(string='Entradas VIP', default=0)
    seat_ids = fields.Many2many(
        'cinenvista.seat',
        string='Butacas Reservadas'
    )
    occupied_seat_ids = fields.Many2many(
        'cinenvista.seat',
        compute='_compute_occupied_seats',
        string='Butacas Ocupadas',
        readonly=True
    )
    available_seat_ids = fields.Many2many(
        'cinenvista.seat',
        compute='_compute_available_seats',
        string='Butacas Disponibles',
        readonly=True
    )
    seat_qty = fields.Integer(
        string='Número de asientos reservados',
        compute='_compute_seat_qty',
        store=True
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('canceled', 'Cancelado'),
    ], string='Estado', default='draft')
    
    # Campo para vincular con el pedido de venta
    sale_order_id = fields.Many2one('sale.order', string='Pedido de venta', readonly=True)

    @api.depends('seat_ids')
    def _compute_seat_qty(self):
        """Calcular el total de asientos según las butacas seleccionadas"""
        for rec in self:
            rec.seat_qty = len(rec.seat_ids)

    @api.depends('screening_id')
    def _compute_occupied_seats(self):
        """Obtener butacas ocupadas para esta sesión"""
        for rec in self:
            if rec.screening_id:
                # Buscar reservas confirmadas para esta sesión
                domain = [
                    ('screening_id', '=', rec.screening_id.id),
                    ('state', '=', 'confirmed'),
                ]
                # Solo excluir si el registro está persistido en BD
                if rec.id and isinstance(rec.id, int):
                    domain.append(('id', '!=', rec.id))
                
                reservations = self.env['cinenvista.reservation'].search(domain)
                rec.occupied_seat_ids = reservations.mapped('seat_ids')
            else:
                rec.occupied_seat_ids = self.env['cinenvista.seat']

    @api.depends('screening_id', 'occupied_seat_ids')
    def _compute_available_seats(self):
        """Obtener butacas disponibles para esta sesión"""
        for rec in self:
            if rec.screening_id and rec.screening_id.room_id:
                # Todas las butacas de la sala menos las ocupadas
                occupied_ids = rec.occupied_seat_ids.ids
                available = self.env['cinenvista.seat'].search([
                    ('room_id', '=', rec.screening_id.room_id.id),
                    ('id', 'not in', occupied_ids)
                ])
                rec.available_seat_ids = available
            else:
                rec.available_seat_ids = self.env['cinenvista.seat']

    @api.model_create_multi
    def create(self, vals_list):
        """Crear reserva sin generar código de ticket (se genera al imprimir)"""
        return super().create(vals_list)

    def action_generate_ticket(self):
        """Generar código de secuencia si no existe y descargar el reporte PDF"""
        for rec in self:
            if not rec.name or rec.name == 'New':
                sequence = self.env['ir.sequence'].next_by_code('cinenvista.reservation')
                rec.name = sequence if sequence else 'TKT/0000'
        action = self.env.ref('cinenvista.action_report_ticket')
        return action.report_action(self, config=False)

    def action_view_sale_order(self):
        """Método para abrir la vista formulario del pedido de venta vinculado"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pedido de Venta'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    def action_confirm_reservation(self):
        """Confirmar reserva: Crear/Confirmar Sale Order y cambiar estado a confirmado"""
        self.ensure_one()
        
        total_seats = len(self.seat_ids)

        # Validar que se hayan seleccionado butacas
        if total_seats <= 0:
            raise ValidationError(_("Debe seleccionar al menos una butaca."))

        # Validar que no haya seleccionado butacas ocupadas
        occupied_ids = self.occupied_seat_ids.ids
        selected_ids = self.seat_ids.ids
        if any(seat_id in occupied_ids for seat_id in selected_ids):
            raise ValidationError(_("Algunas butacas seleccionadas ya están ocupadas. Por favor, selecciona otras."))

        # Si no existe pedido de venta, crear uno
        if not self.sale_order_id:
            sale_order = self.env['sale.order'].create({
                'partner_id': self.partner_id.id,
            })
            
            # Crear líneas de pedido según la cantidad de butacas seleccionadas
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
            
            if order_lines:
                sale_order.write({'order_line': order_lines})
            
            # Confirmar el pedido
            sale_order.action_confirm()
            
            # Vincular al pedido a la reserva
            self.sale_order_id = sale_order.id
        else:
            # Si el pedido ya existe y no está confirmado, confirmarlo
            if self.sale_order_id.state in ['draft', 'sent']:
                self.sale_order_id.action_confirm()
        
        # Cambiar estado de la reserva a confirmado
        self.state = 'confirmed'
        
        return True

    @api.constrains('seat_ids', 'screening_id', 'state')
    def _check_seat_availability(self):
        """Validar disponibilidad de asientos en la sala antes de confirmar"""
        for rec in self:
            if not rec.screening_id or not rec.screening_id.room_id or not rec.seat_ids:
                continue
            capacity = rec.screening_id.room_id.capacity or 0
            total_seats = len(rec.seat_ids)
            
            # Validación de capacidad individual
            if total_seats > capacity:
                raise ValidationError(
                    _('No se pueden reservar más asientos de los que tiene la sala (capacidad: %s).') % capacity
                )
            
            # Validación de ocupación total de la sesión al confirmar
            if rec.state == 'confirmed':
                domain = [('screening_id', '=', rec.screening_id.id), ('state', '=', 'confirmed')]
                existing = self.search(domain).filtered(lambda r: r.id != rec.id)
                total_confirmed = sum(existing.mapped('seat_qty')) or 0
                if (total_confirmed + total_seats) > capacity:
                    raise ValidationError(
                        _('No hay suficientes asientos disponibles para confirmar la reserva.\n'
                          'Capacidad: %s, ya confirmados: %s, solicitados: %s') % (
                            capacity, total_confirmed, total_seats
                        )
                    )
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
    seat_qty = fields.Integer(string='Número de asientos reservados', default=1)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('canceled', 'Cancelado'),
    ], string='Estado', default='draft')
    
    # Campo para vincular con el pedido de venta
    sale_order_id = fields.Many2one('sale.order', string='Pedido de venta', readonly=True)

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

    @api.constrains('seat_qty', 'screening_id', 'state')
    def _check_seat_availability(self):
        """Validar disponibilidad de asientos en la sala antes de confirmar"""
        for rec in self:
            if not rec.screening_id or not rec.screening_id.room_id:
                continue
            capacity = rec.screening_id.room_id.capacity or 0
            
            # Validación de capacidad individual
            if rec.seat_qty and rec.seat_qty > capacity:
                raise ValidationError(
                    _('No se pueden reservar más asientos de los que tiene la sala (capacidad: %s).') % capacity
                )
            
            # Validación de ocupación total de la sesión al confirmar
            if rec.state == 'confirmed':
                domain = [('screening_id', '=', rec.screening_id.id), ('state', '=', 'confirmed')]
                existing = self.search(domain).filtered(lambda r: r.id != rec.id)
                total_confirmed = sum(existing.mapped('seat_qty')) or 0
                if (total_confirmed + (rec.seat_qty or 0)) > capacity:
                    raise ValidationError(
                        _('No hay suficientes asientos disponibles para confirmar la reserva.\n'
                          'Capacidad: %s, ya confirmados: %s, solicitados: %s') % (
                            capacity, total_confirmed, rec.seat_qty or 0
                        )
                    )
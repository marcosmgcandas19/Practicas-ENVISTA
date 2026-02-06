from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CinenvistaReservation(models.Model):
    _name = 'cinenvista.reservation'
    _description = 'Reservas'

    name = fields.Char(
        string='Código de Ticket', 
        default='New',
        copy=False, 
        readonly=True,
        tracking=True
    )
    partner_id = fields.Many2one('res.partner', string='Cliente')
    screening_id = fields.Many2one('cinenvista.screening', string='Sesión', required=True)
    seat_qty = fields.Integer(string='Número de asientos reservados', default=1)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('canceled', 'Cancelado'),
    ], string='Estado', default='draft')
    
    @api.model_create_multi
    def create(self, vals_list):
        """Crear reserva sin generar código de ticket (se genera al imprimir)"""
        return super().create(vals_list)

    def action_generate_ticket(self):
        """Generar código de ticket y hacer download del PDF"""
        # Generar código de secuencia si no lo tiene
        for rec in self:
            if not rec.name or rec.name == 'New':
                sequence = self.env['ir.sequence'].next_by_code('cinenvista.reservation')
                rec.name = sequence if sequence else 'TKT/0000'
        # Generar y descargar el PDF
        action = self.env.ref('cinenvista.action_report_ticket')
        return action.report_action(self, config=False)

    @api.constrains('seat_qty', 'screening_id', 'state')
    def _check_seat_availability(self):
        for rec in self:
            # Si no hay sesión o la sala no tiene capacidad definida, no se realiza la validación
            if not rec.screening_id or not rec.screening_id.room_id:
                continue
            capacity = rec.screening_id.room_id.capacity or 0
            # 1) Una reserva individual no puede solicitar más asientos que la capacidad de la sala
            if rec.seat_qty and rec.seat_qty > capacity:
                raise ValidationError(
                    'No se pueden reservar más asientos de los que tiene la sala (capacidad: %s).' % capacity
                )
            # 2) Al confirmar una reserva, comprobamos que la suma de asientos ya confirmados más los solicitados no supere la capacidad
            if rec.state == 'confirmed':
                domain = [('screening_id', '=', rec.screening_id.id), ('state', '=', 'confirmed')]
                # Buscamos las reservas confirmadas de la misma sesión (excluyendo la reserva actual)
                existing = self.search(domain).filtered(lambda r: r.id != rec.id)
                total_confirmed = sum(existing.mapped('seat_qty')) or 0
                if (total_confirmed + (rec.seat_qty or 0)) > capacity:
                    raise ValidationError(
                        'No hay suficientes asientos disponibles para confirmar la reserva.\n'
                        'Capacidad: %s, ya confirmados: %s, solicitados: %s' % (
                            capacity, total_confirmed, rec.seat_qty or 0
                        )
                    )

    

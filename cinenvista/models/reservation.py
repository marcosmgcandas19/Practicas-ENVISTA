from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CinenvistaReservation(models.Model):
    _name = 'cinenvista.reservation'
    _description = 'Reservas'

    partner_id = fields.Many2one('res.partner', string='Cliente')
    screening_id = fields.Many2one('cinenvista.screening', string='Sesión', required=True)
    seat_qty = fields.Integer(string='Número de asientos reservados', default=1)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('canceled', 'Cancelado'),
    ], string='Estado', default='draft')

    @api.constrains('seat_qty', 'screening_id', 'state')
    def _check_seat_availability(self):
        for rec in self:
            # if no screening or no capacity defined, skip
            if not rec.screening_id or not rec.screening_id.room_id:
                continue
            capacity = rec.screening_id.room_id.capacity or 0
            # 1) A single reservation cannot request more seats than the room capacity
            if rec.seat_qty and rec.seat_qty > capacity:
                raise ValidationError(
                    'No se pueden reservar más asientos de los que tiene la sala (capacidad: %s).' % capacity
                )
            # 2) When a reservation is confirmed, ensure total confirmed seats do not exceed capacity
            if rec.state == 'confirmed':
                domain = [('screening_id', '=', rec.screening_id.id), ('state', '=', 'confirmed')]
                # search confirmed reservations for this screening (exclude current record)
                existing = self.search(domain).filtered(lambda r: r.id != rec.id)
                total_confirmed = sum(existing.mapped('seat_qty')) or 0
                if (total_confirmed + (rec.seat_qty or 0)) > capacity:
                    raise ValidationError(
                        'No hay suficientes asientos disponibles para confirmar la reserva.\n'
                        'Capacidad: %s, ya confirmados: %s, solicitados: %s' % (
                            capacity, total_confirmed, rec.seat_qty or 0
                        )
                    )

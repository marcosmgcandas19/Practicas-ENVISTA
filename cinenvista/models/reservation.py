from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CinenvistaReservation(models.Model):
    _name = 'cinenvista.reservation'
    _description = 'Reservas'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('cinenvista.reservation') or '/')
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
            # Comprobación: El número de asientos no puede ser negativo
            if rec.seat_qty and rec.seat_qty < 0:
                raise ValidationError(
                    'El número de asientos a reservar no puede ser negativo.'
                )
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

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cinenvista.reservation') or '/'
        return super(CinenvistaReservation, self).create(vals)

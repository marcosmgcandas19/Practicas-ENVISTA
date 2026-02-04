from odoo import models, fields, api

class CinenvistaScreening(models.Model):
    _name = 'cinenvista.screening'
    _rec_name = 'name'
    _description = 'Horarios de Proyección'

    movie_id = fields.Many2one('cinenvista.movie', string='Película', required=True)
    room_id = fields.Many2one('cinenvista.room', string='Sala', required=True)
    start_time = fields.Datetime(string='Fecha y Hora de Inicio', required=True)

    name = fields.Char(string='Nombre', compute='_compute_name', store=True)
    reservation_ids = fields.One2many('cinenvista.reservation', 'screening_id', string='Reservas')
    available_seats = fields.Integer(string='Asientos disponibles', compute='_compute_available_seats')

    @api.depends('movie_id.title', 'start_time')
    def _compute_name(self):
        for rec in self:
            title = rec.movie_id.title or ''
            start = rec.start_time or ''
            if title and start:
                rec.name = "%s - %s" % (title, start)
            else:
                rec.name = title or start or False

    @api.depends('reservation_ids.seat_qty', 'reservation_ids.state', 'room_id.capacity')
    def _compute_available_seats(self):
        for rec in self:
            capacity = rec.room_id.capacity or 0
            confirmed = rec.reservation_ids.filtered(lambda r: r.state == 'confirmed')
            reserved = sum(confirmed.mapped('seat_qty'))
            rec.available_seats = max(0, capacity - reserved)
from odoo import models, fields

class CinenvistaScreening(models.Model):
    _name = 'cinenvista.screening'
    _description = 'Horarios de Proyección'

    movie_id = fields.Many2one('cinenvista.movie', string='Película', required=True)
    room_id = fields.Many2one('cinenvista.room', string='Sala', required=True)
    start_time = fields.Datetime(string='Fecha y Hora de Inicio', required=True)
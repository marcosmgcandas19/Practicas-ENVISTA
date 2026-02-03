from odoo import models, fields

class CinenvistaRoom(models.Model):
    _name = 'cinenvista.room'
    _description = 'Salas de Cine'

    name = fields.Char(string='Nombre de la Sala', required=True)
    capacity = fields.Integer(string='Aforo Máximo')
    screening_ids = fields.One2many(
        'cinenvista.screening', 
        'room_id', 
        string='Horarios de Proyección'
    )
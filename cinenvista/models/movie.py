from odoo import models, fields

class CinenvistaMovie(models.Model):
    _name = 'cinenvista.movie'
    _description = 'Modelo para las películas'

    title = fields.Char(string='Título', required=True)
    description = fields.Text(string='Descripción')
    rating = fields.Selection([
        ('0', 'Sin puntuación'),
        ('1', 'Mala'),
        ('2', 'Normal'),
        ('3', 'Buena'),
        ('4', 'Muy buena'),
        ('5', 'Excelente'),
    ], string='Puntuación', default='0')
    image_url = fields.Char(string='URL de la Imagen')
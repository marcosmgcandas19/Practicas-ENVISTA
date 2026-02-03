# -*- coding: utf-8 -*-

from odoo import models, fields

class CinenvistaMovie(models.Model):
    _name = 'cinenvista.movie'
    _description = 'Modelo para las películas'

    title = fields.Char(string='Título', required=True)
    description = fields.Char(string='Descripción')
    rating = fields.Float(string='Puntuación')
    image_url = fields.Char(string='URL de la Imagen')
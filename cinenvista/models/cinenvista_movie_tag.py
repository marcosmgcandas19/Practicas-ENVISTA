# -*- coding: utf-8 -*-
from odoo import models, fields


class CinenvistaMovieTag(models.Model):
    """
    Modelo para gestionar etiquetas de películas.
    Una película puede tener varias etiquetas y una etiqueta contiene muchas películas.
    """
    _name = 'cinenvista.movie.tag'
    _rec_name = 'name'
    _description = 'Etiquetas de películas'

    # ============ CAMPOS ============
    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre de la etiqueta'
    )
    color = fields.Integer(
        string='Color',
        help='Índice numérico de color que Odoo utiliza para asignar una paleta de colores predefinida'
    )

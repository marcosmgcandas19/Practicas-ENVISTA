# -*- coding: utf-8 -*-

from odoo import models, fields


class TojiBook(models.Model):
    """Modelo específico para Libros en la tienda Toji"""
    _inherit = 'product.template'
    _description = 'Libro Toji'

    website_published = fields.Boolean(
        string='Publicado en Web',
        default=False,
        help='Determina si el libro se muestra o no en la web.'
    )
    
    image_url = fields.Char(
        string='URL de Imagen',
        help='Campo para añadir la imagen vía URL.'
    )

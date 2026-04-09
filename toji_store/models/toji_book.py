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

    author_ids = fields.Many2many(
        'res.partner',
        string='Autores',
        domain=[('is_company', '=', False)],
        help='Autores de la obra literaria. Se seleccionan solo contactos de tipo persona.'
    )

    synopsis = fields.Text(
        string='Sinopsis',
        help='Descripción extendida de la obra literaria.'
    )

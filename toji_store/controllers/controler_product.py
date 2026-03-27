# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class TojiProductAPI(http.Controller):
    """API Controller para productos publicados en web"""

    @http.route('/api/toji/products', auth='public', type='json')
    def get_products(self, **kwargs):
        """
        Retorna un arreglo JSON de libros publicados en web.
        
        Campos retornados:
        - id: ID del libro
        - name: Nombre del libro
        - price: Precio de lista
        - image_url: URL de la imagen del libro
        
        Returns:
            dict: {'products': [...]}
        """
        try:
            # Consultar libros con website_published = True
            products = request.env['toji.book'].search([
                ('website_published', '=', True)
            ])
            
            # Construir arreglo con los datos requeridos
            products_data = []
            for product in products:
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.list_price,
                    'image_url': product.image_url,
                })
            
            return {
                'success': True,
                'products': products_data,
                'count': len(products_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'products': []
            }

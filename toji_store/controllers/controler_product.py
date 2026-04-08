# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class TojiProductAPI(http.Controller):
    """API Controller para productos publicados en web"""

    @http.route('/api/toji/products', auth='public', type='http')
    def get_products(self, **kwargs):
        """
        Retorna un arreglo JSON de libros publicados en web.
        
        Campos retornados:
        - id: ID del libro
        - name: Nombre del libro
        - price: Precio de lista
        - image_url: URL de la imagen del libro
        
        Returns:
            JSON Response
        """
        try:
            # Consultar libros con website_published = True
            products = request.env['product.template'].sudo().search([
                ('website_published', '=', True)
            ])
            
            # Construir arreglo con los datos requeridos
            products_data = []
            for product in products:
                # Obtener URL de imagen
                image_url = ''
                if product.image_url:
                    image_url = product.image_url
                elif product.image_1920:
                    # Usar imagen del template si existe
                    image_url = f"/web/image/product.template/{product.id}/image_1920"
                
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.list_price) if product.list_price else 0.0,
                    'image_url': image_url,
                })
            
            response_data = {
                'success': True,
                'products': products_data,
                'count': len(products_data)
            }
            
            # Retornar JSON con headers CORS
            headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
            
            return request.make_response(
                json.dumps(response_data),
                headers=headers
            )
            
        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e),
                'products': [],
                'count': 0
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
            
            return request.make_response(
                json.dumps(response_data),
                headers=headers
            )

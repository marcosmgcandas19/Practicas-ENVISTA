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

    @http.route('/api/toji/products/<int:product_id>', auth='public', type='json')
    def get_product_detail(self, product_id, **kwargs):
        """
        Retorna los detalles de un producto individual publicado en web.
        
        URL: GET/POST /api/toji/products/<product_id>
        
        Args:
            product_id (int): ID del producto a obtener
        
        Returns:
            JSON con los siguientes campos:
            - id: ID del producto
            - name: Nombre del producto
            - price: Precio de lista
            - description: Descripción del producto
            - synopsis: Sinopsis literaria
            - authors: Lista de autores con id y name
            - image_url: URL de la imagen del producto
            - website_published: Estado de publicación en web
        """
        try:
            print(f"\n[DEBUG] Buscando producto con ID: {product_id}, tipo: {type(product_id)}")
            
            # Buscar el producto que coincida con el ID y esté publicado
            product = request.env['product.template'].sudo().search([
                ('id', '=', product_id),
                ('website_published', '=', True)
            ], limit=1)
            
            print(f"[DEBUG] Producto encontrado: {bool(product)}")
            
            # Si no encuentra con website_published, buscar sin esa condición para debuguear
            if not product:
                print(f"[DEBUG] No encontrado con website_published=True, buscando sin esa condición...")
                product_debug = request.env['product.template'].sudo().search([
                    ('id', '=', product_id)
                ], limit=1)
                if product_debug:
                    print(f"[DEBUG] Producto existe pero website_published={product_debug.website_published}")
                else:
                    print(f"[DEBUG] Producto NO existe en la BD")
            
            # Validar que el producto existe
            if not product:
                return {
                    'success': False,
                    'error': 'Producto no encontrado o no publicado',
                    'product': None
                }
            
            # Obtener URL de imagen
            image_url = ''
            if product.image_url:
                image_url = product.image_url
            elif product.image_1920:
                image_url = f"/web/image/product.template/{product.id}/image_1920"
            
            # Construir lista de autores
            authors_data = []
            for author in product.author_ids:
                authors_data.append({
                    'id': author.id,
                    'name': author.name,
                })
            
            # Construir respuesta con los detalles del producto
            product_data = {
                'id': product.id,
                'name': product.name,
                'price': float(product.list_price) if product.list_price else 0.0,
                'description': product.description or '',
                'synopsis': product.synopsis or '',
                'authors': authors_data,
                'image_url': image_url,
                'website_published': product.website_published,
            }
            
            print(f"[DEBUG] Retornando producto exitosamente: {product.name}")
            
            return {
                'success': True,
                'product': product_data
            }
            
        except Exception as e:
            print(f"[DEBUG] Error en get_product_detail: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'product': None
            }


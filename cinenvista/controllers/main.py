# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import csv
import os
from datetime import date

_logger = logging.getLogger(__name__)

def get_color_mapping():
    """
    Lee el archivo CSV de etiquetas de películas y crea un mapeo de color numérico a hexadecimal.
    """
    color_mapping = {
        1: '#EF5350', 2: '#FB8C00', 3: '#FDD835', 4: '#42A5F5',
        5: '#AB47BC', 6: '#EC407A', 7: '#8D6E63', 8: '#BDBDBD',
        9: '#00897B', 10: '#2ECC71', 11: '#3F51B5',
    }
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cinenvista.movie.tag.csv')
    
    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        color_num = int(row.get('color', 0))
                    except (ValueError, TypeError):
                        pass
    except Exception as e:
        _logger.warning(f"[CINENVISTA] No se pudo leer CSV de colores: {str(e)}")
    
    return color_mapping

class CinenvistaCineController(http.Controller):
    
    # ============ MÉTODOS PRIVADOS REUTILIZABLES ============
    
    def _get_tags_with_colors(self, tags, color_map):
        tags_list = []
        for tag in tags:
            hex_color = color_map.get(tag.color, '#BDBDBD')
            tags_list.append({
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'hex_color': hex_color,
            })
        return tags_list
    
    def _convert_movie_to_dict(self, movie, include_colors=False):
        movie_dict = {
            'id': movie.id,
            'title': movie.title or 'Sin título',
            'description': movie.description or '',
            'rating': movie.rating or 0.0,
            'image_url': movie.image_url or '',
            'release_date': movie.release_date,
            'duration': movie.duration,
            'state': movie.state or 'draft',
        }
        if include_colors:
            color_map = get_color_mapping()
            movie_dict['tag_ids'] = self._get_tags_with_colors(movie.tag_ids, color_map)
        else:
            movie_dict['tag_ids'] = [{'id': tag.id, 'name': tag.name} for tag in movie.tag_ids]
        return movie_dict

    def _convert_screening_to_dict(self, screening):
        return {
            'id': screening.id,
            'start_time': screening.start_time,
            'room_id': screening.room_id.id,
            'room_name': screening.room_id.name,
            'available_seats': screening.available_seats,
        }
    
    def _get_screenings_today(self, movie_id):
        today = date.today()
        screenings_orm = request.env['cinenvista.screening'].sudo().search([
            ('movie_id', '=', movie_id),
            ('start_time', '>=', f'{today} 00:00:00'),
            ('start_time', '<=', f'{today} 23:59:59'),
        ], order='start_time asc')
        return [self._convert_screening_to_dict(s) for s in screenings_orm]

    # ============ RUTAS PÚBLICAS (VISTAS) ============
    
    @http.route('/cine', auth='public', website=True)
    def home(self, **kw):
        movies_orm = request.env['cinenvista.movie'].sudo().search([])
        movies_data = [self._convert_movie_to_dict(m, include_colors=True) for m in movies_orm]
        return request.render('cinenvista.home_template', {
            'movies': movies_data,
            'total_movies': len(movies_data),
        })

    @http.route('/cine/pelicula/<model("cinenvista.movie"):movie>', auth='public', website=True)
    def movie_detail(self, movie, **kw):
        movie_dict = self._convert_movie_to_dict(movie, include_colors=True)
        screenings_data = self._get_screenings_today(movie.id)
        return request.render('cinenvista.movie_template', {
            'movie': movie_dict,
            'screenings': screenings_data,
        })

    # ============ API DE RESERVA (JSON/AJAX) ============

    @http.route('/cine/api/session/<int:session_id>/seats', type='http', auth='public', website=True, methods=['GET'])
    def get_session_seats(self, session_id, **kw):
        """ 
        Endpoint de obtención de butacas: Retorna mapa de sala y disponibilidad.
        
        Args:
            session_id (int): ID de la sesión de proyección
            
        Returns:
            json: Contiene session_id y lista de butacas con su estado (ocupada/disponible)
        """
        try:
            screening = request.env['cinenvista.screening'].sudo().browse(session_id)
            if not screening.exists():
                return request.make_json_response({'error': 'Sesión no encontrada', 'success': False}, status=404)

            # Buscar todas las butacas de la sala
            all_seats = request.env['cinenvista.seat'].sudo().search([
                ('room_id', '=', screening.room_id.id)
            ], order='row, number')
            
            # Obtener las butacas ocupadas por reservas confirmadas
            confirmed_reservations = request.env['cinenvista.reservation'].sudo().search([
                ('screening_id', '=', session_id),
                ('state', '=', 'confirmed')
            ])
            occupied_ids = confirmed_reservations.mapped('seat_ids').ids

            # Construir lista de butacas con estado
            seats_data = [{
                'id': seat.id,
                'name': seat.name,
                'row': seat.row,
                'number': seat.number,
                'is_occupied': seat.id in occupied_ids
            } for seat in all_seats]

            result = {
                'success': True,
                'session_id': session_id,
                'seats': seats_data,
                'room_name': screening.room_id.name,
                'movie_title': screening.movie_id.title,
                'screening_time': screening.start_time.isoformat() if screening.start_time else None
            }
            
            return request.make_json_response(result)
            
        except Exception as e:
            _logger.error(f'[CINENVISTA] Error al obtener butacas: {str(e)}')
            return request.make_json_response({'error': 'Error al obtener el mapa de butacas', 'success': False}, status=500)

    @http.route('/cine/api/session/reserve', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def reserve_seats(self, **kw):
        """ 
        Endpoint de Confirmación: Crea Pedido de Venta y Reserva.
        Extrae los parámetros del body JSON.
        
        Returns:
            json: Contiene 'success' (bool), y si es exitoso: order_id y reservation_name
        """
        try:
            import json
            
            # Extraer datos del body JSON
            request_data = request.get_json_data()
            session_id = request_data.get('session_id')
            seat_ids = request_data.get('seat_ids', [])
            
            _logger.info(f'[CINENVISTA] Iniciando reserva - session_id: {session_id}, seat_ids: {seat_ids}')
            
            # Validación de entrada
            if not session_id or not isinstance(session_id, int):
                msg = 'ID de sesión inválido'
                _logger.warning(f'[CINENVISTA] {msg} - session_id: {session_id}')
                return request.make_json_response({'success': False, 'message': msg}, status=400)
            
            if not seat_ids or not isinstance(seat_ids, list):
                msg = 'No hay asientos seleccionados'
                _logger.warning(f'[CINENVISTA] {msg} - seat_ids: {seat_ids}')
                return request.make_json_response({'success': False, 'message': msg}, status=400)

            seat_ids = [int(sid) for sid in seat_ids]  # Asegurar que son enteros
            _logger.info(f'[CINENVISTA] IDs convertidos a enteros: {seat_ids}')

            # Obtener la sesión
            screening = request.env['cinenvista.screening'].sudo().browse(session_id)
            if not screening.exists():
                msg = 'Sesión no encontrada'
                _logger.warning(f'[CINENVISTA] {msg} - session_id: {session_id}')
                return request.make_json_response({'success': False, 'message': msg}, status=404)
            
            _logger.info(f'[CINENVISTA] Sesión encontrada: {screening.name} - Sala: {screening.room_id.name}')

            # Validar que todas las butacas existen y pertenecen a la sala
            seats = request.env['cinenvista.seat'].sudo().browse(seat_ids)
            invalid_seats = [s for s in seats if s.room_id.id != screening.room_id.id]
            if len(seats) != len(seat_ids) or invalid_seats:
                msg = 'Una o más butacas seleccionadas no son válidas'
                _logger.warning(f'[CINENVISTA] {msg} - Butacas encontradas: {len(seats)}, esperadas: {len(seat_ids)}')
                return request.make_json_response({'success': False, 'message': msg}, status=400)

            _logger.info(f'[CINENVISTA] Butacas validadas: {seats.mapped("name")}')

            # Verificar que las butacas no estén ya ocupadas
            occupied_seats = request.env['cinenvista.reservation'].sudo().search([
                ('screening_id', '=', screening.id),
                ('state', '=', 'confirmed'),
                ('seat_ids', 'in', seat_ids)
            ])
            if occupied_seats:
                occupied_names = list(set(occupied_seats.mapped('seat_ids.name')))
                msg = f'Las siguientes butacas ya están reservadas: {", ".join(occupied_names)}'
                _logger.warning(f'[CINENVISTA] {msg}')
                return request.make_json_response({'success': False, 'message': msg}, status=409)

            # Obtener producto de entrada regular
            product = request.env['product.product'].sudo().search([('name', 'ilike', 'Entrada Regular')], limit=1)
            if not product:
                msg = 'Producto de entrada no configurado en el sistema'
                _logger.warning(f'[CINENVISTA] {msg}')
                return request.make_json_response({'success': False, 'message': msg}, status=500)

            _logger.info(f'[CINENVISTA] Producto encontrado: {product.name} - Precio: {product.list_price}')

            # Obtener el usuario actual (partner)
            partner_id = request.env.user.partner_id.id if request.env.user.partner_id else False
            _logger.info(f'[CINENVISTA] Partner ID: {partner_id}')
            
            # Crear Pedido de Venta (sale.order)
            order_vals = {
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': len(seat_ids),
                    'price_unit': product.list_price or 0.0,
                    'name': f"Entrada: {screening.movie_id.title} ({screening.start_time.strftime('%d/%m/%Y %H:%M')})",
                })],
            }
            if partner_id:
                order_vals['partner_id'] = partner_id
                
            _logger.info(f'[CINENVISTA] Creando pedido de venta con {len(seat_ids)} líneas')
            order = request.env['sale.order'].sudo().create(order_vals)
            _logger.info(f'[CINENVISTA] Pedido creado: {order.name} (ID: {order.id})')

            # Crear Reserva (cinenvista.reservation)
            _logger.info(f'[CINENVISTA] Creando reserva con seat_ids: {seat_ids}')
            reservation = request.env['cinenvista.reservation'].sudo().create({
                'screening_id': screening.id,
                'seat_ids': [(6, 0, seat_ids)],
                'sale_order_id': order.id,
                'state': 'confirmed',
                'partner_id': partner_id if partner_id else False,
            })
            _logger.info(f'[CINENVISTA] Reserva creada: {reservation.name} (ID: {reservation.id})')

            result = {
                'success': True, 
                'order_id': order.id, 
                'reservation_name': reservation.name,
                'message': f'Reserva confirmada para las butacas: {", ".join(seats.mapped("name"))}'
            }
            
            return request.make_json_response(result)

        except json.JSONDecodeError as e:
            _logger.error(f'[CINENVISTA] Error al parsear JSON: {str(e)}', exc_info=True)
            return request.make_json_response({'success': False, 'message': f'JSON inválido: {str(e)}'}, status=400)
        except ValueError as e:
            _logger.error(f'[CINENVISTA] Error de validación en reserva: {str(e)}', exc_info=True)
            return request.make_json_response({'success': False, 'message': f'Datos inválidos: {str(e)}'}, status=400)
        except Exception as e:
            _logger.error(f'[CINENVISTA] Error al procesar reserva: {str(e)}', exc_info=True)
            return request.make_json_response({'success': False, 'message': f'Error: {str(e)}'}, status=500)
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

    @http.route('/cine/api/session/<int:session_id>/seats', type='json', auth='public', website=True)
    def get_session_seats(self, session_id, **kw):
        """ Endpoint de obtención de butacas: Retorna mapa de sala y disponibilidad. """
        screening = request.env['cinenvista.screening'].sudo().browse(session_id)
        if not screening.exists():
            return {'error': 'Sesión no encontrada'}

        # Buscar butacas de la sala
        all_seats = request.env['cinenvista.seat'].sudo().search([('room_id', '=', screening.room_id.id)])
        
        # Cruzar con reservas confirmadas
        confirmed_reservations = request.env['cinenvista.reservation'].sudo().search([
            ('screening_id', '=', session_id),
            ('state', '=', 'confirmed')
        ])
        occupied_ids = confirmed_reservations.mapped('seat_ids').ids

        seats_data = [{
            'id': seat.id,
            'name': seat.name,
            'row': seat.row,
            'number': seat.number,
            'is_occupied': seat.id in occupied_ids
        } for seat in all_seats]

        return {'session_id': session_id, 'seats': seats_data}

    @http.route('/cine/api/session/reserve', type='json', auth='public', website=True, methods=['POST'])
    def reserve_seats(self, session_id, seat_ids, **kw):
        """ Endpoint de Confirmación: Crea Pedido de Venta y Reserva. """
        if not seat_ids:
            return {'success': False, 'message': 'No hay asientos seleccionados'}

        screening = request.env['cinenvista.screening'].sudo().browse(session_id)
        
        # 1. Obtener producto de entrada
        product = request.env['product.product'].sudo().search([('name', 'ilike', 'Entrada Regular')], limit=1)
        if not product:
            return {'success': False, 'message': 'Producto de entrada no configurado'}

        # 2. Crear Pedido de Venta (sale.order)
        order = request.env['sale.order'].sudo().create({
            'partner_id': request.env.user.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': len(seat_ids),
                'price_unit': product.list_price,
                'name': f"Entrada: {screening.movie_id.title} ({screening.start_time})",
            })],
        })

        # 3. Crear Reserva (cinenvista.reservation)
        reservation = request.env['cinenvista.reservation'].sudo().create({
            'screening_id': session_id,
            'seat_ids': [(6, 0, seat_ids)],
            'sale_order_id': order.id,
            'state': 'confirmed',
            'partner_id': request.env.user.partner_id.id,
        })

        return {'success': True, 'order_id': order.id, 'reservation_name': reservation.display_name}
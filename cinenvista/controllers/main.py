# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import csv
import os

_logger = logging.getLogger(__name__)


def get_color_mapping():
    """
    Lee el archivo CSV de etiquetas de películas y crea un mapeo de color numérico a hexadecimal.
    Valores estándar para colores 1-11 de Odoo.
    """
    color_mapping = {
        1: '#EF5350',      # Rojo
        2: '#FB8C00',      # Naranja
        3: '#FDD835',      # Amarillo
        4: '#42A5F5',      # Azul Claro
        5: '#AB47BC',      # Púrpura
        6: '#EC407A',      # Rosa
        7: '#8D6E63',      # Marrón
        8: '#BDBDBD',      # Gris
        9: '#00897B',      # Verde Azulado
        10: '#2ECC71',     # Verde
        11: '#3F51B5',     # Índigo
    }
    
    # Ruta del archivo CSV
    csv_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'data',
        'cinenvista.movie.tag.csv'
    )
    
    # Intentar leer colores únicos del CSV
    try:
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                unique_colors = set()
                for row in reader:
                    try:
                        color_num = int(row.get('color', 0))
                        if color_num > 0:
                            unique_colors.add(color_num)
                    except (ValueError, TypeError):
                        pass
                
                _logger.info(f"[CINENVISTA] Colores únicos encontrados en CSV: {sorted(unique_colors)}")
    except Exception as e:
        _logger.warning(f"[CINENVISTA] No se pudo leer CSV de colores: {str(e)}")
    
    return color_mapping


class CinenvistaCineController(http.Controller):
    
    # ============ MÉTODOS PRIVADOS REUTILIZABLES ============
    
    def _get_tags_with_colors(self, tags, color_map):
        """
        Convierte una colección de tags con sus colores hexadecimales.
        
        Args:
            tags: Colección ORM de tags
            color_map (dict): Mapeo de color numérico a hexadecimal
            
        Returns:
            list: Lista de diccionarios de tags con colores
        """
        tags_list = []
        for tag_idx, tag in enumerate(tags, 1):
            hex_color = color_map.get(tag.color, '#BDBDBD')
            tag_dict = {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'hex_color': hex_color,
            }
            tags_list.append(tag_dict)
            _logger.info(f"    TAG {tag_idx}: {tag.name} (Color: {tag.color} → {hex_color})")
        return tags_list
    
    def _convert_movie_to_dict(self, movie, include_colors=False):
        """
        Convierte un objeto ORM de película a diccionario.
        
        Args:
            movie: Objeto ORM cinenvista.movie
            include_colors (bool): Si True, incluye tags con colores hexadecimales
            
        Returns:
            dict: Película en formato diccionario
        """
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
        
        # Procesar tags
        if include_colors:
            color_map = get_color_mapping()
            tags_list = self._get_tags_with_colors(movie.tag_ids, color_map)
            movie_dict['tag_ids'] = tags_list
            movie_dict['tag_count'] = len(tags_list)
        else:
            movie_dict['tag_ids'] = [{'id': tag.id, 'name': tag.name} for tag in movie.tag_ids]
        
        return movie_dict
    
    def _convert_screening_to_dict(self, screening):
        """
        Convierte un objeto ORM de sesión/screening a diccionario.
        
        Args:
            screening: Objeto ORM cinenvista.screening
            
        Returns:
            dict: Sesión en formato diccionario
        """
        return {
            'id': screening.id,
            'start_time': screening.start_time,
            'room_id': screening.room_id.id,
            'room_name': screening.room_id.name,
            'available_seats': screening.available_seats,
        }
    
    def _get_screenings_today(self, movie_id):
        """
        Obtiene todas las sesiones de una película programadas para hoy.
        
        Args:
            movie_id (int): ID de la película
            
        Returns:
            list: Lista de diccionarios de sesiones ordenadas por hora
        """
        from datetime import date
        today = date.today()
        
        screenings_orm = request.env['cinenvista.screening'].sudo().search([
            ('movie_id', '=', movie_id),
            ('start_time', '>=', f'{today} 00:00:00'),
            ('start_time', '<', f'{today} 23:59:59'),
            ('is_future', '=', True),
        ], order='start_time asc')
        
        _logger.info(f"[CINENVISTA] Sesiones encontradas para hoy: {len(screenings_orm)}")
        
        screenings_data = []
        for screening in screenings_orm:
            screening_dict = self._convert_screening_to_dict(screening)
            screenings_data.append(screening_dict)
            _logger.info(f"  - Sesión {screening.id}: {screening.start_time} en {screening.room_id.name}")
        
        return screenings_data
    
    # ============ RUTAS PÚBLICAS ============
    
    @http.route('/cine', auth='public', website=True)
    def home(self, **kw):
        """
        Controlador Principal - Renderizado de la Home.
        Ruta: /cine (Página de inicio principal del módulo)
        """
        _logger.info("=" * 80)
        _logger.info("[CINENVISTA] ✓ RUTA /cine ACCEDIDA")
        _logger.info("=" * 80)
        
        # Obtener todas las películas
        movies_orm = request.env['cinenvista.movie'].sudo().search([])
        _logger.info(f"[CINENVISTA] Total películas ORM encontradas: {len(movies_orm)}")
        
        # Conversión ORM → Diccionarios
        movies_data = []
        for idx, movie in enumerate(movies_orm, 1):
            _logger.info(f"\n[PELÍCULA {idx}]")
            _logger.info(f"  ID: {movie.id}")
            _logger.info(f"  TITLE: '{movie.title}'")
            _logger.info(f"  RATING: {movie.rating}")
            _logger.info(f"  IMAGE_URL: '{movie.image_url}'")
            _logger.info(f"  TAG_IDS COUNT: {len(movie.tag_ids)}")
            
            movie_dict = self._convert_movie_to_dict(movie, include_colors=True)
            movies_data.append(movie_dict)
            _logger.info(f"  ✓ Película {idx} convertida correctamente")
        
        _logger.info(f"\n[CINENVISTA] Total películas convertidas: {len(movies_data)}")
        
        # Preparar valores
        values = {
            'movies': movies_data,
            'total_movies': len(movies_data),
        }
        
        _logger.info(f"[CINENVISTA] Estructura de datos a renderizar:")
        _logger.info(f"  - 'movies': {type(values['movies']).__name__} con {len(values['movies'])} elementos")
        _logger.info(f"  - 'total_movies': {values['total_movies']}")
        if values['movies']:
            first = values['movies'][0]
            _logger.info(f"  - Primera película keys: {list(first.keys())}")
            _logger.info(f"  - Primera película 'title': {first['title']}")
            _logger.info(f"  - Primera película 'rating': {first['rating']}")
            _logger.info(f"  - Primera película 'image_url': {first['image_url']}")
            _logger.info(f"  - Primera película 'tag_ids': {first['tag_ids']}")
        
        _logger.info(f"[CINENVISTA] ✓ Renderizando template: cinenvista.home_template")
        
        return request.render('cinenvista.home_template', values)


    @http.route('/cine/pelicula/<model("cinenvista.movie"):movie>', auth='public', website=True)
    def movie_detail(self, movie, **kw):
        """
        Controlador de Detalle de Película.
        Ruta: /cine/pelicula/<id_película> (Página de detalles de película individual)
        
        Recibe un objeto de película y obtiene las sesiones programadas para hoy.
        """
        _logger.info("=" * 80)
        _logger.info(f"[CINENVISTA] ✓ RUTA /cine/pelicula/<movie> ACCEDIDA")
        _logger.info(f"[CINENVISTA] Película solicitada: {movie.title} (ID: {movie.id})")
        _logger.info("=" * 80)
        
        # Convertir película y obtener sesiones
        movie_dict = self._convert_movie_to_dict(movie, include_colors=False)
        screenings_data = self._get_screenings_today(movie.id)
        
        # Preparar valores para renderizar
        values = {
            'movie': movie_dict,
            'screenings': screenings_data,
            'total_screenings': len(screenings_data),
        }
        
        _logger.info(f"[CINENVISTA] Estructura de datos:")
        _logger.info(f"  - Película: {movie_dict['title']}")
        _logger.info(f"  - Sesiones de hoy: {len(screenings_data)}")
        _logger.info(f"[CINENVISTA] ✓ Renderizando template: cinenvista.movie_template")
        
        return request.render('cinenvista.movie_template', values)

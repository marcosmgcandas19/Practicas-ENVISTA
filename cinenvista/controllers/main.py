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
    
    @http.route('/cine', auth='public', website=True)
    def home(self, **kw):
        """
        Controlador Principal - Renderizado de la Home.
        Ruta: /cine (Página de inicio principal del módulo)
        """
        _logger.info("=" * 80)
        _logger.info("[CINENVISTA] ✓ RUTA /cine ACCEDIDA")
        _logger.info("=" * 80)
        
        # Obtener mapeo de colores desde el CSV
        color_map = get_color_mapping()
        
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
            
            # Extraer etiquetas
            tags_list = []
            for tag_idx, tag in enumerate(movie.tag_ids, 1):
                # Obtener color hexadecimal del mapeo (leído dinámicamente del CSV)
                hex_color = color_map.get(tag.color, '#BDBDBD')  # Gris por defecto
                tag_dict = {
                    'id': tag.id,
                    'name': tag.name,
                    'color': tag.color,
                    'hex_color': hex_color,
                }
                tags_list.append(tag_dict)
                _logger.info(f"    TAG {tag_idx}: {tag.name} (Color: {tag.color} → {hex_color})")
            
            # Crear diccionario de película
            movie_dict = {
                'id': movie.id,
                'title': movie.title or 'Sin título',
                'description': movie.description or '',
                'rating': movie.rating or 0.0,
                'image_url': movie.image_url or '',
                'state': movie.state or 'draft',
                'tag_ids': tags_list,
                'tag_count': len(tags_list),
            }
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
        _logger.info("=" * 80 + "\n")
        
        return request.render('cinenvista.home_template', values)

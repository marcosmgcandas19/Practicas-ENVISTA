# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class CinenvistaMovie(models.Model):
    """
    Modelo para gestionar Películas.
    Integración con TMDB (The Movie Database) para obtener datos automáticamente:
    títulos, descripciones, puntuaciones, carátulas, duración, etc.
    """
    _name = 'cinenvista.movie'
    _rec_name = 'title'
    _description = 'Modelo para las películas'

    # ============ CAMPOS BÁSICOS ============
    title = fields.Char(
        string='Título',
        required=True,
        help='Título de la película'
    )
    description = fields.Text(
        string='Descripción',
        help='Sinopsis o descripción detallada de la película'
    )
    rating = fields.Float(
        string='Puntuación',
        default=0.0,
        help='Puntuación de 0 a 10 (obtenida de TMDB)'
    )
    tag_ids = fields.Many2many(
        'cinenvista.movie.tag',
        string='Etiquetas',
        help='Etiquetas asociadas a la película'
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('coming_soon', 'Próximamente'),
            ('in_theaters', 'En Cartelera'),
            ('archived', 'Retirada'),
        ],
        string='Estado',
        default='draft',
        help='Estado actual de la película'
    )
    
    # ============ CAMPOS DE INTEGRACIÓN EXTERNA ============
    image_url = fields.Char(
        string='URL de la Imagen',
        help='URL del cartel/póster de la película (de TMDB)'
    )
    tmdb_id = fields.Char(
        string='ID de TMDB',
        help='ID único de la película en The Movie Database'
    )
    release_date = fields.Date(
        string='Fecha de Estreno',
        help='Fecha de estreno de la película'
    )
    duration = fields.Float(
        string='Duración',
        help='Duración de la película en minutos'
    )

    # ============ CONFIGURACIÓN DE BÚSQUEDA TMDB ============
    TMDB_API_KEY = '70cb72743febfe5e2748a5e323bee131'
    TMDB_SEARCH_URL = 'https://api.themoviedb.org/3/search/movie'
    TMDB_DETAILS_URL = 'https://api.themoviedb.org/3/movie/'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

    # ============ MÉTODOS DE INTEGRACIÓN TMDB ============
    def _search_movie_data(self):
        """ Busca datos de película en TMDB usando el título actual. """
        if not self.title:
            return

        try:
            self._perform_tmdb_request()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Error de conexión con TMDB: {str(e)}')
        except Exception as e:
            _logger.error(f'Error al procesar datos de película: {str(e)}')

    def _perform_tmdb_request(self):
        """ Realiza la solicitud a la API de búsqueda y luego a la de detalles para la duración. """
        params = {
            'api_key': self.TMDB_API_KEY,
            'query': self.title,
            'language': 'es-ES'
        }

        # 1. Llamada de búsqueda para obtener el ID
        response = requests.get(self.TMDB_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get('results', [])
        if not results:
            _logger.info(f'No se encontraron resultados en TMDB para: {self.title}')
            return

        movie_data = results[0]
        tmdb_id = movie_data.get('id')

        # 2. Llamada de detalles para obtener 'runtime' (duración)
        if tmdb_id:
            try:
                details_res = requests.get(
                    f"{self.TMDB_DETAILS_URL}{tmdb_id}",
                    params={'api_key': self.TMDB_API_KEY, 'language': 'es-ES'},
                    timeout=10
                )
                if details_res.status_code == 200:
                    # Mezclamos los datos (el runtime viene aquí)
                    movie_data.update(details_res.json())
            except Exception as e:
                _logger.warning(f"No se pudo obtener la duración para ID {tmdb_id}: {e}")

        self._update_fields_from_tmdb(movie_data)

    def _update_fields_from_tmdb(self, movie_data):
        """ Actualiza los campos del modelo con datos procesados. """
        self.title = movie_data.get('title', self.title)
        self.description = movie_data.get('overview', '')
        self.rating = float(movie_data.get('vote_average', 0.0))
        self.tmdb_id = str(movie_data.get('id', ''))
        
        # Mapear fecha de estreno
        release_date_str = movie_data.get('release_date')
        if release_date_str:
            self.release_date = release_date_str
        
        # Mapear duración (runtime en TMDB son minutos)
        duration_value = movie_data.get('runtime')
        if duration_value:
            self.duration = float(duration_value)
            _logger.info(f"DEBUG CINENVISTA: Mapeando duración -> {self.duration} min")

        # Construir URL de imagen
        poster_path = movie_data.get('poster_path')
        if poster_path:
            self.image_url = f"{self.TMDB_IMAGE_BASE_URL}{poster_path}"

        _logger.info(f'Película cargada y actualizada desde TMDB: {self.title}')

    # ============ EVENTOS Y ACCIONES ============
    @api.onchange('title')
    def _onchange_title(self):
        """ Dispara la búsqueda al cambiar el título en el formulario. """
        self._search_movie_data()

    def action_get_movie(self):
        """ Acción de botón para forzar la actualización de datos. """
        self._search_movie_data()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sincronización TMDB',
                'message': f'Datos de "{self.title}" actualizados correctamente.',
                'type': 'success',
                'sticky': False,
            }
        }
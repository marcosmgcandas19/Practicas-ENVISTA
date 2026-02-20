from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class CinenvistaMovie(models.Model):
    """
    Modelo para gestionar Películas.
    Integración con TMDB (The Movie Database) para obtener datos automáticamente:
    títulos, descripciones, puntuaciones, carátulas, etc.
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
    
    # ============ CAMPOS DE INTEGRACIÓN EXTERNA ============
    image_url = fields.Char(
        string='URL de la Imagen',
        help='URL del cartel/póster de la película (de TMDB)'
    )
    tmdb_id = fields.Char(
        string='ID de TMDB',
        help='ID único de la película en The Movie Database'
    )

    # ============ CONFIGURACIÓN DE BÚSQUEDA TMDB ============
    # Constantes de la API (considerar llevarlas a settings en producción)
    TMDB_API_KEY = '70cb72743febfe5e2748a5e323bee131'
    TMDB_SEARCH_URL = 'https://api.themoviedb.org/3/search/movie'
    TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

    # ============ MÉTODOS DE INTEGRACIÓN TMDB ============
    def _search_movie_data(self):
        """
        Busca datos de película en TMDB usando el título actual.
        Rellena automáticamente: descripción, puntuación, imagen y ID de TMDB.
        Si no encuentra resultados, simplemente ignora (no produce error).
        """
        if not self.title:
            return

        try:
            self._perform_tmdb_request()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Error de conexión con TMDB: {str(e)}')
        except Exception as e:
            _logger.error(f'Error al procesar datos de película: {str(e)}')

    def _perform_tmdb_request(self):
        """
        Realiza la solicitud HTTP a TMDB y procesa la respuesta.
        Separa la lógica de red de la de procesamiento de datos.
        """
        params = {
            'api_key': self.TMDB_API_KEY,
            'query': self.title,
            'language': 'es-ES'
        }

        response = requests.get(
            self.TMDB_SEARCH_URL,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        results = data.get('results', [])
        if not results:
            _logger.info(f'No se encontraron resultados en TMDB para: {self.title}')
            return

        self._update_fields_from_tmdb(results[0])

    def _update_fields_from_tmdb(self, movie_data):
        """
        Actualiza los campos del modelo con datos obtenidos de TMDB.
        
        Args:
            movie_data (dict): Diccionario con datos de película de TMDB API
        """
        self.title = movie_data.get('title', '')
        self.description = movie_data.get('overview', '')
        self.rating = float(movie_data.get('vote_average', 0.0))
        self.tmdb_id = str(movie_data.get('id', ''))

        # Construir URL completa de la imagen
        poster_path = movie_data.get('poster_path')
        if poster_path:
            self.image_url = f"{self.TMDB_IMAGE_BASE_URL}{poster_path}"

        _logger.info(f'Película cargada desde TMDB: {self.title}')

    # ============ EVENTOS Y ACCIONES ============
    @api.onchange('title')
    def _onchange_title(self):
        """
        Al cambiar el título, busca automáticamente datos en TMDB.
        Esto permite llenar campos mientras el usuario escribe.
        """
        self._search_movie_data()

    def action_get_movie(self):
        """
        Acción llamada por un botón en la interfaz.
        Busca película en TMDB y notifica al usuario.
        """
        self._search_movie_data()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Búsqueda',
                'message': f'Datos de "{self.title}" cargados desde TMDB',
                'type': 'info',
                'sticky': False,
            }
        }
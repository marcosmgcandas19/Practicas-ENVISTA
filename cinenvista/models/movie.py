from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class CinenvistaMovie(models.Model):
    _name = 'cinenvista.movie'
    _rec_name = 'title'
    _description = 'Modelo para las películas'

    title = fields.Char(string='Título', required=True)
    description = fields.Text(string='Descripción')
    rating = fields.Float(string='Puntuación', default=0.0, help='Puntuación de 0 a 10')
    image_url = fields.Char(string='URL de la Imagen')
    tmdb_id = fields.Char(string='ID de TMDB', help='ID de la película en The Movie Database')

    def _search_movie_data(self):
        """Busca datos de película en TMDB y rellena los campos"""
        if not self.title:
            return

        API_KEY = '70cb72743febfe5e2748a5e323bee131'
        URL = 'https://api.themoviedb.org/3/search/movie'

        params = {
            'api_key': API_KEY,
            'query': self.title,
            'language': 'es-ES'
        }

        try:
            response = requests.get(URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get('results', [])
            if not results:
                return

            movie = results[0]

            # Rellena los campos del formulario
            self.title = movie.get('title', '')
            self.description = movie.get('overview', '')
            self.rating = float(movie.get('vote_average', 0.0))
            self.tmdb_id = str(movie.get('id', ''))

            # Construir URL de la imagen
            if movie.get('poster_path'):
                self.image_url = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}"

            _logger.info(f'Película encontrada: {self.title}')

        except requests.exceptions.RequestException as e:
            _logger.error(f'Error de conexión con TMDB: {str(e)}')
        except Exception as e:
            _logger.error(f'Error al procesar datos: {str(e)}')

    @api.onchange('title')
    def _onchange_title(self):
        """Busca automáticamente al cambiar el título"""
        self._search_movie_data()

    def action_get_movie(self):
        """Método llamado por el botón para buscar película"""
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
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

    def action_get_movie(self):
        
        if not self.title:
            raise UserError('Debes ingresar un título de película antes de buscar')
        
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
            
            # Obtener el primer resultado
            results = data.get('results', [])
            if not results:
                raise UserError(f'No se encontró película con el título "{self.title}"')
            
            movie = results[0]
            
            # Mapear los campos de la API con nuestro modelo
            # title (Char) = title
            # description (Text) = overview
            # rating (Float) = vote_average
            # image_url (Char) = https://image.tmdb.org/t/p/w500 + poster_path
            
            self.title = movie.get('title', self.title)
            self.description = movie.get('overview', '')
            self.rating = float(movie.get('vote_average', 0.0))
            
            # Construir la URL de la imagen
            poster_path = movie.get('poster_path')
            if poster_path:
                self.image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            
            # Guardar el ID de TMDB
            self.tmdb_id = str(movie.get('id', ''))
            
            _logger.info(f'Película actualizada desde TMDB: {self.title}')
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Éxito',
                    'message': f'Película "{self.title}" cargada correctamente desde TMDB',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error(f'Error en la API de TMDB: {str(e)}')
            raise UserError(f'Error al conectar con TMDB: {str(e)}')
        except Exception as e:
            _logger.error(f'Error inesperado: {str(e)}')
            raise UserError(f'Error inesperado: {str(e)}')
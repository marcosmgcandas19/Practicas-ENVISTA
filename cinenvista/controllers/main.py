# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CinenvistaCineController(http.Controller):
    
    @http.route('/cine', auth='public', website=True)
    def home(self, **kw):
        """
        Controlador Principal - Renderizado de la Home.
        Ruta: /cine (Página de inicio principal del módulo)
        
        Lógica de Consulta (ORM): 
        - Utiliza .sudo() para saltar las restricciones de acceso del usuario público.
        - Realiza búsqueda sobre el modelo cinenvista.movie.
        
        Renderizado:
        - Retorna la plantilla QWeb 'cinenvista.home_template' con los registros de películas.
        """
        # Obtener todas las películas usando sudo() para acceso público
        movies = request.env['cinenvista.movie'].sudo().search([])
        
        # Preparar los valores a pasar a la plantilla
        values = {
            'movies': movies,
        }
        
        # Renderizar y retornar la plantilla QWeb
        return request.render('cinenvista.home_template', values)

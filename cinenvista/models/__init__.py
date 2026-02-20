# -*- coding: utf-8 -*-
"""
Importación de modelos del módulo CinenVista.

Modelos disponibles:
- cinenvista_movie: Gestión de películas con integración TMDB
- cinenvista_movie_tag: Etiquetas de películas
- cinenvista_room: Salas y butacas de cine
- cinenvista_screening: Sesiones/proyecciones
- cinenvista_reservation: Reservas de entradas
- cinenvista_res_partner: Extensión de contactos con fidelización
"""

from . import cinenvista_movie
from . import cinenvista_movie_tag
from . import cinenvista_room
from . import room_seat
from . import cinenvista_screening
from . import cinenvista_res_partner
from . import cinenvista_reservation
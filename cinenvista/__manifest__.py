{
    'name': 'CinenVista',
    'version': '1.0',
    'summary': 'Gestión de películas y Fax en contactos',
    'category': 'Services',
    'author': 'Tu Nombre',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/movie_views.xml',
        'views/room_views.xml',
        'views/screening_views.xml',
        'views/res_partner_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
}
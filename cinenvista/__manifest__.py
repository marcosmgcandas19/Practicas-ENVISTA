{
    'name': 'CinenVista',
    'version': '1.0',
    'summary': 'Gestión de películas y Fax en contactos',
    'category': 'Services',
    'author': 'Marcos',
    'depends': ['base', 'contacts', 'product', 'sale'],
    'data': [
        'data/product.product.csv',
        'data/cinenvista_sequence_tickets.xml',
        'security/ir.model.access.csv',
        'views/cinenvista_movie.xml',
        'views/cinenvista_room.xml',
        'views/cinenvista_screening.xml',
        'views/cinenvista_reservation.xml',
        'views/cinenvista_res_partner.xml',
        'views/cinenvista_views.xml',
        'views/cinenvista_menus.xml',
        'views/cinenvista_report_ticket_template.xml',
        'wizards/cinenvista_ticket_wizard.xml',
    ],
    'installable': True,
    'application': True,
    'external_dependencies': {
        'python': ['requests'],
    }
}
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
        'views/res_partner.xml',
        'views/cinenvista_seat.xml',
        'reports/report_ticket_template.xml',
        'wizards/cinenvista_ticket_wizard.xml',
        'views/cinenvista_menus.xml',
    ],
    
    'installable': True,
    'application': True,
    'external_dependencies': {
        'python': ['requests'],
    }
}
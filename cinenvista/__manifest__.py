{
    # ============ INFORMACIÓN BÁSICA DEL MÓDULO ============
    'name': 'CinenVista',
    'version': '1.0',
    'summary': 'Sistema completo de gestión integral para cines. Incluye películas, salas, sesiones, reservas y programa de fidelización.',
    'category': 'Services',
    'author': 'Marcos',
    
    # ============ DEPENDENCIAS ============
    'depends': [
        'base',          # Módulo base de Odoo
        'contacts',      # Para extender res.partner con fidelización
        'product',       # Para crear productos de entradas
        'sale',          # Para crear órdenes de venta
    ],
    
    # ============ ARCHIVOS DE DATOS Y VISTAS ============
    'data': [
        # Datos iniciales
        'data/product.product.csv',                    # Productos: Entrada Regular, VIP
        'data/cinenvista_sequence_tickets.xml',        # Secuencia para códigos de ticket
        'data/cinenvista.movie.tag.csv',               # Etiquetas de películas
        
        # Seguridad y permisos
        'security/ir.model.access.csv',                # Control de acceso a modelos
        
        # Vistas del backend
        'views/cinenvista_movie.xml',                  # Películas
        'views/cinenvista_movie_tag.xml',              # Etiquetas de películas
        'views/cinenvista_room.xml',                   # Salas
        'views/cinenvista_screening.xml',              # Sesiones de proyección
        'views/cinenvista_reservation.xml',            # Reservas
        'views/res_partner.xml',                       # Extensión de contactos con lealtad
        'views/cinenvista_seat.xml',                   # Butacas
        
        # Reportes
        'reports/report_ticket_template.xml',          # Reporte PDF de tickets
        
        # Asistentes
        'wizards/cinenvista_ticket_wizard.xml',        # Asistente de venta rápida
        
        # Menús
        'views/cinenvista_menus.xml',                  # Menús de navegación
    ],
    
    # ============ CONFIGURACIÓN DE INSTALACIÓN ============
    'installable': True,
    'application': True,
    
    # ============ DEPENDENCIAS EXTERNAS ============
    'external_dependencies': {
        'python': ['requests'],  # Para integraciones con TMDB (películas)
    }
}
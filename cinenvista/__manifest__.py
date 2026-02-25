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
    # El orden es crítico: Seguridad -> Datos -> Vistas -> Menús
    'data': [
        # 1. Seguridad y permisos (Indispensable cargar primero)
        'security/groups.xml',                         # Categoría y Grupos de seguridad
        'security/ir.model.access.csv',                # Control de acceso (ACL)
        'security/rules.xml',                          # Reglas de registro (Record Rules)
        
        # 2. Configuración técnica
        'data/cinenvista_sequence_tickets.xml',        # Secuencia para códigos de ticket
        
        # 3. Carga de datos maestros (CSV)
        # Se cargan aquí para que Odoo ya conozca los modelos y permisos
        'data/product.product.csv',                    # Productos: Entrada Regular, VIP
        'data/cinenvista.movie.tag.csv',               # Etiquetas de películas
        
        # 4. Vistas del backend (Definición de la interfaz)
        'views/cinenvista_movie.xml',                  # Películas
        'views/cinenvista_movie_tag.xml',              # Etiquetas
        'views/cinenvista_room.xml',                   # Salas
        'views/cinenvista_screening.xml',              # Sesiones
        'views/cinenvista_reservation.xml',            # Reservas
        'views/res_partner.xml',                       # Extensión de contactos
        'views/cinenvista_seat.xml',                   # Butacas
        
        # 5. Reportes y Wizards
        'reports/report_ticket_template.xml',          # Reporte PDF de tickets
        'wizards/cinenvista_ticket_wizard.xml',        # Asistente de venta rápida
        
        # 6. Menús (Siempre al final para que las acciones ya existan)
        'views/cinenvista_menus.xml',                  # Menús de navegación
    ],
    
    # ============ CONFIGURACIÓN DE INSTALACIÓN ============
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # ============ DEPENDENCIAS EXTERNAS ============
    'external_dependencies': {
        'python': ['requests'],  # Para integraciones con TMDB
    }
}
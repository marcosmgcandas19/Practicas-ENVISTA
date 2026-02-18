from odoo import models, fields, api


class CinenvistaRoom(models.Model):
    """
    Modelo para gestionar Salas de Cine.
    Una sala tiene dimensiones (filas x columnas), capacidad máxima,
    y genera automáticamente butacas individuales.
    """
    _name = 'cinenvista.room'
    _description = 'Salas de Cine'

    # ============ CAMPOS BÁSICOS ============
    name = fields.Char(
        string='Nombre de la Sala',
        required=True,
        help='Identificador de la sala (ej: Sala 1, VIP, 3D, etc.)'
    )
    capacity = fields.Integer(
        string='Aforo Máximo',
        help='Total de asientos en la sala (calculado automáticamente)'
    )
    
    # ============ CONFIGURACIÓN DE DIMENSIONES ============
    rows_qty = fields.Integer(
        string='Cantidad de filas',
        default=10,
        help='Número de filas de butacas (A, B, C, ..., Z, AA, AB, ...)'
    )
    cols_qty = fields.Integer(
        string='Butacas por fila',
        default=10,
        help='Número de asientos en cada fila'
    )

    # ============ RELACIONES ============
    screening_ids = fields.One2many(
        'cinenvista.screening',
        'room_id',
        string='Horarios de Proyección',
        help='Sesiones/proyecciones programadas en esta sala'
    )
    seat_ids = fields.One2many(
        'cinenvista.seat',
        'room_id',
        string='Listado de butacas',
        help='Todas las butacas individuales de la sala'
    )

    # ============ MÉTODOS DE CONFIGURACIÓN ============
    def action_generate_seats(self):
        """
        Genera automáticamente todas las butacas de la sala.
        Pasos:
        1. Elimina las butacas existentes
        2. Crea nuevas butacas con nomenclatura: Fila+Número (A1, A2, B1, B2, etc.)
        3. Actualiza la capacidad automáticamente
        
        Usado cuando se cambian dimensiones de la sala.
        """
        for room in self:
            # Paso 1: Eliminar butacas existentes
            room.seat_ids.unlink()

            # Paso 2: Generar lista de butacas a crear
            seats_to_create = self._generate_seats_list(room)

            # Paso 3: Creación masiva (optimizado para rendimiento)
            if seats_to_create:
                self.env['cinenvista.seat'].create(seats_to_create)
            
            # Paso 4: Actualizar capacidad
            room.capacity = len(seats_to_create)
        
        return True

    @staticmethod
    def _generate_seats_list(room):
        """
        Genera la estructura de datos para crear todas las butacas.
        
        Args:
            room: Instancia de la sala
            
        Returns:
            list: Lista de diccionarios con datos para crear butacas
            
        Ejemplo: rows=2, cols=3 genera: A1, A2, A3, B1, B2, B3
        """
        seats = []
        
        for i in range(room.rows_qty):
            # Convertir índice a letra (0→A, 1→B, 2→C, etc.)
            row_letter = chr(65 + i)
            
            # Crear butacas 1 a cols_qty para esta fila
            for j in range(1, room.cols_qty + 1):
                seats.append({
                    'row': row_letter,
                    'number': j,
                    'room_id': room.id,
                })
        
        return seats
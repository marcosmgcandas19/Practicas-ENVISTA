from odoo import models, fields, api

class CinenvistaRoom(models.Model):
    _name = 'cinenvista.room'
    _description = 'Salas de Cine'

    name = fields.Char(string='Nombre de la Sala', required=True)
    capacity = fields.Integer(string='Aforo Máximo')
    
    rows_qty = fields.Integer(string='Cantidad de filas', default=10)
    cols_qty = fields.Integer(string='Butacas por fila', default=10)
    
    screening_ids = fields.One2many(
        'cinenvista.screening', 
        'room_id', 
        string='Horarios de Proyección'
    )

    seat_ids = fields.One2many(
        'cinenvista.seat', 
        'room_id', 
        string='Listado de butacas'
    )

    def action_generate_seats(self):
        for room in self:
            # 1. Borrar (unlink) las butacas existentes
            room.seat_ids.unlink()

            # 2. Generar datos mediante bucles
            seats_to_create = []
            for i in range(room.rows_qty):
                # chr(65) es 'A', chr(66) es 'B', etc.
                row_letter = chr(65 + i)
                
                for j in range(1, room.cols_qty + 1):
                    seats_to_create.append({
                        'row': row_letter,
                        'number': j,
                        'room_id': room.id,
                    })

            # 3. Creación masiva para optimizar rendimiento
            if seats_to_create:
                self.env['cinenvista.seat'].create(seats_to_create)
        
        return True
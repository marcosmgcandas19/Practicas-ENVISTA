from odoo import models, fields, api


class CinenvistaScreening(models.Model):
    """
    Modelo de Horarios de Proyección de Cine.
    Representa cada sesión: película, sala, hora de inicio.
    Calcula automáticamente los asientos disponibles según reservas confirmadas.
    """
    _name = 'cinenvista.screening'
    _rec_name = 'name'
    _description = 'Horarios de Proyección'

    # ============ CAMPOS BÁSICOS ============
    movie_id = fields.Many2one(
        'cinenvista.movie',
        string='Película',
        required=True,
        help='Película que se proyecta en esta sesión'
    )
    room_id = fields.Many2one(
        'cinenvista.room',
        string='Sala',
        required=True,
        help='Sala de cine donde se proyecta la sessión'
    )
    start_time = fields.Datetime(
        string='Fecha y Hora de Inicio',
        required=True,
        help='Fecha y hora en que inicia la proyección'
    )

    # ============ CAMPOS CALCULADOS ============
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
        store=True,
        help='Identificador automático: "Película - Hora"'
    )
    available_seats = fields.Integer(
        string='Asientos disponibles',
        compute='_compute_available_seats',
        help='Total de asientos disponibles en esta sesión'
    )

    # ============ RELACIONES ============
    reservation_ids = fields.One2many(
        'cinenvista.reservation',
        'screening_id',
        string='Reservas',
        help='Reservas realizadas para esta sesión'
    )

    # ============ MÉTODOS COMPUTADOS ============
    @api.depends('movie_id.title', 'start_time')
    def _compute_name(self):
        """
        Calcula el nombre de la sesión: "Película - Fecha/Hora".
        Se utiliza para mostrar identificadores legibles en toda la interfaz.
        """
        for record in self:
            title = record.movie_id.title or ''
            start = record.start_time or ''
            if title and start:
                record.name = "%s - %s" % (title, start)
            else:
                record.name = title or start or False

    @api.depends('reservation_ids.seat_qty', 'reservation_ids.state', 'room_id.capacity')
    def _compute_available_seats(self):
        """
        Calcula asientos disponibles: Capacidad - (Asientos de reservas confirmadas).
        Se recalcula automáticamente cuando:
        - Se confirma/cancela una reserva
        - Cambia la capacidad de la sala
        """
        for record in self:
            capacity = record.room_id.capacity or 0
            # Sumar solo asientos de reservas confirmadas
            confirmed = record.reservation_ids.filtered(lambda r: r.state == 'confirmed')
            reserved = sum(confirmed.mapped('seat_qty'))
            record.available_seats = max(0, capacity - reserved)
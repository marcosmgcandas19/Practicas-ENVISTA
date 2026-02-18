from odoo import models, fields, api


class CinenVistaSeat(models.Model):
    """
    Modelo para representar una butaca individual en una sala.
    Cada butaca tiene una identificación única: Fila (letra) + Número.
    Ejemplo: A1, B5, Z10, etc.
    """
    _name = 'cinenvista.seat'
    _description = 'Butaca de Cine'

    # ============ CAMPOS BÁSICOS ============
    row = fields.Char(
        string='Fila',
        required=True,
        help='Letra de la fila (A, B, C, ..., Z)'
    )
    number = fields.Integer(
        string='Número de asiento',
        required=True,
        help='Número de posición en la fila (1, 2, 3, ...)'
    )

    # ============ RELACIONES ============
    room_id = fields.Many2one(
        'cinenvista.room',
        string='Sala',
        ondelete='cascade',
        required=True,
        help='Sala a la que pertenece esta butaca'
    )

    # ============ CAMPOS CALCULADOS ============
    name = fields.Char(
        string='Código de butaca',
        compute='_compute_name',
        store=True,
        help='Identificador único: Fila+Número (ej: A1, B5)'
    )

    # ============ MÉTODOS COMPUTADOS ============
    @api.depends('row', 'number')
    def _compute_name(self):
        """
        Calcula el código único de la butaca combinando fila y número.
        Ejemplo: fila=A, número=1 → name=A1
        """
        for record in self:
            if record.row and record.number:
                record.name = f"{record.row}{record.number}"
            else:
                record.name = "/"
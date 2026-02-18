from odoo import models, fields, api


class ResPartner(models.Model):
    """
    Extensión del modelo res.partner con campos de fidelización.
    Agrega sistema de niveles de membresía y puntos de lealtad.
    """
    _inherit = 'res.partner'

    # ============ CAMPOS HEREDADOS (COMPATIBILIDAD) ============
    # Campos que permanecen por compatibilidad con instalaciones anteriores
    fax = fields.Char(
        string='Fax',
        help='Campo heredado (compatibilidad con versiones anteriores)'
    )
    global_location_number = fields.Char(
        string='Global Location Number',
        help='Campo heredado (compatibilidad con versiones anteriores)'
    )

    # ============ CAMPOS DE FIDELIZACIÓN ============
    member_level = fields.Selection(
        [
            ('standard', 'Estándar'),
            ('silver', 'Platino'),
            ('premium', 'Premium')
        ],
        string='Nivel de Miembro',
        default='standard',
        help='Nivel de membresía según puntos acumulados'
    )
    loyalty_points = fields.Integer(
        string='Puntos de Lealtad',
        default=0,
        help='Puntos acumulados: +10 por compra, -100/-200 por canje'
    )

    # ============ RELACIONES ============
    reservation_ids = fields.One2many(
        'cinenvista.reservation',
        'partner_id',
        string='Reservas',
        help='Todas las reservas realizadas por este cliente'
    )

    # ============ CAMPOS CALCULADOS ============
    reservation_count = fields.Integer(
        string='Número de reservas',
        compute='_compute_reservation_count',
        store=True,
        help='Total de reservas realizadas por el cliente'
    )

    # ============ MÉTODOS COMPUTADOS ============
    @api.depends('reservation_ids')
    def _compute_reservation_count(self):
        """
        Calcula el total de reservas realizadas por este cliente.
        Se actualiza automáticamente cuando se crean/eliminan reservas.
        """
        for record in self:
            record.reservation_count = len(record.reservation_ids)
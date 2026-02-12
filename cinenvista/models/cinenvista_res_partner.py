from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'


    fax = fields.Char(string='Fax')
    global_location_number = fields.Char(string='Global Location Number')
   
    # Campos de Fidelización
    member_level = fields.Selection([
        ('standard', 'Estándar'),
        ('silver', 'Platino'),
        ('premium', 'Premium')
    ], string='Nivel de Miembro', default='standard')
   
    loyalty_points = fields.Integer(string='Puntos de Lealtad', default=0)
   
    # Relación y Contador de Reservas
    reservation_ids = fields.One2many(
        'cinenvista.reservation',
        'partner_id',
        string='Reservas'
    )
    reservation_count = fields.Integer(
        string='Número de reservas',
        compute='_compute_reservation_count',
        store=True
    )


    @api.depends('reservation_ids')
    def _compute_reservation_count(self):
        """Calcula el total de registros en la relación One2many"""
        for rec in self:
            rec.reservation_count = len(rec.reservation_ids)
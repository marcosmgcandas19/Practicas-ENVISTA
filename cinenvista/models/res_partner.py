from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    fax = fields.Char(string='Fax')
    reservation_ids = fields.One2many('cinenvista.reservation', 'partner_id', string='Reservas')
    reservation_count = fields.Integer(string='Número de reservas', compute='_compute_reservation_count')

    @api.depends('reservation_ids')
    def _compute_reservation_count(self):
        for rec in self:
            rec.reservation_count = len(rec.reservation_ids) 
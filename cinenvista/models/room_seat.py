from odoo import models, fields, api

class CinenVistaSeat(models.Model):
    _name = 'cinenvista.seat'
    _description = 'Butaca de Cine'

    row = fields.Char(string='Fila', required=True)
    number = fields.Integer(string='Número de asiento', required=True)
    room_id = fields.Many2one('cinenvista.room', string='Sala', ondelete='cascade', required=True)
    
    name = fields.Char(string='Código de butaca', compute='_compute_name', store=True)

    @api.depends('row', 'number')
    def _compute_name(self):
        for record in self:
            if record.row and record.number:
                record.name = f"{record.row}{record.number}"
            else:
                record.name = "/"
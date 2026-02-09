from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CinenvistaTicketWizard(models.TransientModel):
    _name = 'cinenvista.ticket.wizard'
    _description = 'Asistente de Venta Rápida de Entradas'

    screening_id = fields.Many2one('cinenvista.screening', string='Sesión', required=True)
    seats = fields.Integer(string='Número de asientos', required=True, default=1)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)

    def action_confirm_sale(self):
        """Confirmar venta y crear reserva en estado confirmado"""
        self.ensure_one()
        
        # Validar número de asientos
        if self.seats <= 0:
            raise ValidationError(_("El número de asientos debe ser mayor que cero."))

        # 1. Verificar disponibilidad de asientos
        if self.seats > self.screening_id.available_seats:
            raise ValidationError(
                _("No hay suficientes asientos disponibles.\n"
                  "Asientos disponibles: %s\n"
                  "Asientos solicitados: %s") % (
                    self.screening_id.available_seats, 
                    self.seats
                )
            )

        # 2. Crear reserva directamente en estado confirmado
        self.env['cinenvista.reservation'].create({
            'screening_id': self.screening_id.id,
            'partner_id': self.partner_id.id,
            'seat_qty': self.seats,
            'state': 'confirmed',
        })

        return {'type': 'ir.actions.act_window_close'}
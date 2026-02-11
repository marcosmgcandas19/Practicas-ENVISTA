from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CinenvistaTicketWizard(models.TransientModel):
    _name = 'cinenvista.ticket.wizard'
    _description = 'Asistente de Venta Rápida de Entradas'

    screening_id = fields.Many2one('cinenvista.screening', string='Sesión', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    qty_regular = fields.Integer(string='Entradas regulares', default=0)
    qty_vip = fields.Integer(string='Entradas VIP', default=0)

    def action_confirm_sale(self):
        """Confirmar venta: Crear Sale Order, Confirmar y Vincular Reserva"""
        self.ensure_one()
        
        total_seats = self.qty_regular + self.qty_vip

        # 1. Verificar disponibilidad de asientos
        if total_seats <= 0:
            raise ValidationError(_("Debe seleccionar al menos una entrada."))

        if total_seats > self.screening_id.available_seats:
            raise ValidationError(
                _("No hay suficientes asientos disponibles. Libres: %s, Solicitados: %s") % (
                    self.screening_id.available_seats, 
                    total_seats
                )
            )

        # 2. Crear pedido de venta (sale.order)
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'order_line': [],
        })

        # 3. Añadir líneas de pedido según cantidades
        order_lines = []
        
        if self.qty_regular > 0:
            product_reg = self.env.ref('cinenvista.product_ticket_regular')
            order_lines.append((0, 0, {
                'product_id': product_reg.id,
                'product_uom_qty': self.qty_regular,
            }))

        if self.qty_vip > 0:
            product_vip = self.env.ref('cinenvista.product_ticket_vip')
            order_lines.append((0, 0, {
                'product_id': product_vip.id,
                'product_uom_qty': self.qty_vip,
            }))

        sale_order.write({'order_line': order_lines})

        # 4. Confirmar el pedido
        sale_order.action_confirm()

        # 5. Crear la reserva relacionada
        self.env['cinenvista.reservation'].create({
            'screening_id': self.screening_id.id,
            'partner_id': self.partner_id.id,
            'qty_regular': self.qty_regular,
            'qty_vip': self.qty_vip,
            'state': 'confirmed',
            'sale_order_id': sale_order.id,
        })

        return {'type': 'ir.actions.act_window_close'}
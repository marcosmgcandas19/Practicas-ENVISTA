from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CinenvistaReservation(models.Model):
    _name = 'cinenvista.reservation'
    _description = 'Reservas'

    name = fields.Char(
        string='Código de Ticket', 
        copy=False, 
        readonly=True,
        tracking=True,
        index=True
    )
    partner_id = fields.Many2one('res.partner', string='Cliente')
    screening_id = fields.Many2one('cinenvista.screening', string='Sesión', required=True)
    seat_qty = fields.Integer(string='Número de asientos reservados', default=1)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('canceled', 'Cancelado'),
    ], string='Estado', default='draft')
    
    @api.model_create_multi
    def create(self, vals_list):
        """Crear reserva y generar código de ticket si está confirmada"""
        for vals in vals_list:
            # Si la reserva se crea en estado 'confirmed', generar el código de ticket automáticamente
            if vals.get('state') == 'confirmed' and not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('cinenvista.reservation')
        return super().create(vals_list)

    def write(self, vals):
        """Generar código de ticket cuando se cambia a estado confirmado"""
        # Si se está cambiando el estado a 'confirmed', generar secuencia para los que no lo tengan
        if vals.get('state') == 'confirmed':
            for rec in self:
                # Si el registro actual NO tiene nombre y NO estamos poniendo uno en vals
                if not rec.name and 'name' not in vals:
                    vals = dict(vals)  # Copiar para no modificar el dict original
                    vals['name'] = self.env['ir.sequence'].next_by_code('cinenvista.reservation')
                    break  # Solo hacer esto una vez, el super().write lo hará para todos
        
        return super().write(vals)

    def action_generate_ticket(self):
        """Generar código de ticket (si no lo tiene) y descargar PDF"""
        # Generar código de secuencia si no lo tiene
        for rec in self:
            if not rec.name:
                rec.write({
                    'name': self.env['ir.sequence'].next_by_code('cinenvista.reservation')
                })
        # Generar y descargar el PDF
        action = self.env.ref('cinenvista.action_report_ticket')
        return action.report_action(self, config=False)

    @api.constrains('seat_qty', 'screening_id', 'state')
    def _check_seat_availability(self):
        for rec in self:
            # Si no hay sesión o la sala no tiene capacidad definida, no se realiza la validación
            if not rec.screening_id or not rec.screening_id.room_id:
                continue
            capacity = rec.screening_id.room_id.capacity or 0
            # 1) Una reserva individual no puede solicitar más asientos que la capacidad de la sala
            if rec.seat_qty and rec.seat_qty > capacity:
                raise ValidationError(
                    'No se pueden reservar más asientos de los que tiene la sala (capacidad: %s).' % capacity
                )
            # 2) Al confirmar una reserva, comprobamos que la suma de asientos ya confirmados más los solicitados no supere la capacidad
            if rec.state == 'confirmed':
                domain = [('screening_id', '=', rec.screening_id.id), ('state', '=', 'confirmed')]
                # Buscamos las reservas confirmadas de la misma sesión (excluyendo la reserva actual)
                existing = self.search(domain).filtered(lambda r: r.id != rec.id)
                total_confirmed = sum(existing.mapped('seat_qty')) or 0
                if (total_confirmed + (rec.seat_qty or 0)) > capacity:
                    raise ValidationError(
                        'No hay suficientes asientos disponibles para confirmar la reserva.\n'
                        'Capacidad: %s, ya confirmados: %s, solicitados: %s' % (
                            capacity, total_confirmed, rec.seat_qty or 0
                        )
                    )

    

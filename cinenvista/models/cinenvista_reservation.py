from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CinenvistaReservation(models.Model):
    """
    Modelo de Reserva de Entradas de Cine.
    Gestiona la creación, confirmación y cancelación de reservas.
    Integrado con el sistema de fidelización y puntos de lealtad.
    Regla de oro: Si tiene sale_order_id, vino del wizard (puntos ya procesados).
    """
    _name = 'cinenvista.reservation'
    _description = 'Reservas de Entradas de Cine'

    # ============ CAMPOS BÁSICOS ============
    name = fields.Char(
        string='Código de Ticket',
        default='New',
        copy=False,
        readonly=True,
        help='Identificador único de la reserva/ticket'
    )
    
    # ============ RELACIONES ============
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        help='Cliente que realiza la reserva'
    )
    screening_id = fields.Many2one(
        'cinenvista.screening',
        string='Sesión',
        required=True,
        help='Sesión de cine a la que corresponde la reserva'
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido de venta',
        readonly=True,
        help='Pedido de venta generado por esta reserva (si vino del wizard)'
    )
    
    # ============ CANTIDADES DE ENTRADAS ============
    qty_regular = fields.Integer(
        string='Entradas regulares',
        default=0,
        help='Cantidad de entradas regulares en esta reserva'
    )
    qty_vip = fields.Integer(
        string='Entradas VIP',
        default=0,
        help='Cantidad de entradas VIP en esta reserva'
    )
    
    # ============ BUTACAS ============
    seat_ids = fields.Many2many(
        'cinenvista.seat',
        string='Butacas Reservadas',
        help='Butacas específicas reservadas para esta reserva'
    )
    occupied_seat_ids = fields.Many2many(
        'cinenvista.seat',
        compute='_compute_occupied_seats',
        string='Butacas Ocupadas',
        readonly=True,
        help='Butacas ocupadas por otras reservas confirmadas en la misma sesión'
    )
    available_seat_ids = fields.Many2many(
        'cinenvista.seat',
        compute='_compute_available_seats',
        string='Butacas Disponibles',
        readonly=True,
        help='Butacas disponibles para seleccionar en la misma sesión'
    )
    seat_qty = fields.Integer(
        string='Número de asientos reservados',
        compute='_compute_seat_qty',
        store=True,
        help='Total de asientos reservados (derivado de seat_ids)'
    )
    
    # ============ ESTADO ============
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('canceled', 'Cancelado'),
        ],
        string='Estado',
        default='draft',
        help='Estado actual de la reserva'
    )

    # ============ MÉTODOS COMPUTADOS ============
    @api.depends('seat_ids')
    def _compute_seat_qty(self):
        """Calcula el total de asientos reservados."""
        for record in self:
            record.seat_qty = len(record.seat_ids)

    @api.depends('screening_id')
    def _compute_occupied_seats(self):
        """
        Obtiene las butacas ocupadas por otras reservas confirmadas
        en la misma sesión.
        """
        for record in self:
            if record.screening_id:
                domain = [
                    ('screening_id', '=', record.screening_id.id),
                    ('state', '=', 'confirmed'),
                ]
                # Excluir esta reserva si ya existe en BD
                if record.id and isinstance(record.id, int):
                    domain.append(('id', '!=', record.id))
                
                reservations = self.env['cinenvista.reservation'].search(domain)
                record.occupied_seat_ids = reservations.mapped('seat_ids')
            else:
                record.occupied_seat_ids = self.env['cinenvista.seat']

    @api.depends('screening_id', 'occupied_seat_ids')
    def _compute_available_seats(self):
        """
        Obtiene las butacas disponibles en la sala
        (todas las butacas menos las ocupadas).
        """
        for record in self:
            if record.screening_id and record.screening_id.room_id:
                occupied_ids = record.occupied_seat_ids.ids
                available = self.env['cinenvista.seat'].search([
                    ('room_id', '=', record.screening_id.room_id.id),
                    ('id', 'not in', occupied_ids)
                ])
                record.available_seat_ids = available
            else:
                record.available_seat_ids = self.env['cinenvista.seat']

    # ============ MÉTODOS CICLO DE VIDA ============
    @api.model_create_multi
    def create(self, vals_list):
        """
        Crea reservas y procesa puntos de lealtad si es necesario.
        
        REGLA CLAVE: Si tiene sale_order_id → el wizard ya procesó los puntos.
        Si NO tiene sale_order_id → procesar puntos aquí.
        """
        records = super().create(vals_list)
        
        for record in records:
            # Saltar si viene del wizard (tiene sale_order_id)
            if record.sale_order_id:
                continue
            
            # Procesar puntos para reservas confirmadas creadas directamente
            if record.state == 'confirmed' and record.partner_id and record.seat_ids:
                self._process_loyalty_points(record)
        
        return records

    def write(self, vals):
        """
        Actualiza reservas y procesa puntos si el estado cambia a confirmado.
        
        REGLA CLAVE: Si la reserva tiene sale_order_id, NO procesar puntos
        (ya fueron procesados por el wizard al crear la reserva).
        """
        result = super().write(vals)
        
        # Solo procesar si el estado cambia a confirmado
        if 'state' in vals and vals['state'] == 'confirmed':
            for record in self:
                # Saltar si tiene sale_order_id (procesada por wizard)
                if record.sale_order_id:
                    continue
                
                # Procesar puntos si tiene datos de cliente y asientos
                if record.partner_id and record.seat_ids:
                    self._process_loyalty_points(record)
        
        return result

    # ============ MÉTODOS DE LEALTAD Y PUNTOS ============
    def _process_loyalty_points(self, record):
        """
        Procesa la adición de puntos de lealtad al cliente.
        10 puntos por cada entrada reservada.
        
        Args:
            record: La reserva a procesar
        """
        points_earned = len(record.seat_ids) * 10
        new_total_points = record.partner_id.loyalty_points + points_earned
        new_level = self._calculate_member_level(new_total_points)
        
        record.partner_id.write({
            'loyalty_points': new_total_points,
            'member_level': new_level
        })

    @staticmethod
    def _calculate_member_level(points):
        """
        Calcula el nivel de membresía según puntos.
        - Premium: > 1000
        - Silver: > 500
        - Standard: <= 500
        """
        if points > 1000:
            return 'premium'
        elif points > 500:
            return 'silver'
        else:
            return 'standard'

    # ============ ACCIONES DE USUARIO ============
    def action_generate_ticket(self):
        """
        Genera un código de ticket único para cada reserva
        y descarga el reporte PDF.
        """
        for record in self:
            if not record.name or record.name == 'New':
                sequence = self.env['ir.sequence'].next_by_code('cinenvista.reservation')
                record.name = sequence if sequence else 'TKT/0000'
        
        action = self.env.ref('cinenvista.action_report_ticket')
        return action.report_action(self, config=False)

    def action_view_sale_order(self):
        """Abre el pedido de venta vinculado a esta reserva."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Pedido de Venta'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    def action_confirm_reservation(self):
        """
        Confirma la reserva:
        1. Valida disponibilidad de asientos
        2. Crea/confirma el pedido de venta si no existe
        3. Suma puntos de lealtad
        4. Cambia estado a confirmado
        """
        self.ensure_one()
        
        # Validaciones
        self._validate_reservation_confirmation()
        
        # Gestionar pedido de venta
        if not self.sale_order_id:
            self._create_sale_order()
        else:
            self._confirm_existing_sale_order()
        
        # Procesar lealtad y cambiar estado
        total_seats = len(self.seat_ids)
        self._process_loyalty_points(self)
        
        self.with_context(skip_loyalty_points=True).write({
            'state': 'confirmed',
        })
        
        return True

    # ============ MÉTODOS AUXILIARES ============
    def _validate_reservation_confirmation(self):
        """Valida que la reserva pueda ser confirmada."""
        # Verificar que existan asientos seleccionados
        if not self.seat_ids:
            raise ValidationError(_("Debe seleccionar al menos una butaca."))
        
        # Verificar que los asientos no estén ocupados
        occupied_ids = self.occupied_seat_ids.ids
        selected_ids = self.seat_ids.ids
        
        if any(seat_id in occupied_ids for seat_id in selected_ids):
            raise ValidationError(
                _("Algunas butacas seleccionadas ya están ocupadas.  "
                  "Por favor, selecciona otras.")
            )

    def _create_sale_order(self):
        """Crea un nuevo pedido de venta para esta reserva."""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })
        
        order_lines = self._prepare_sale_order_lines()
        
        if order_lines:
            sale_order.write({'order_line': order_lines})
        
        sale_order.action_confirm()
        self.sale_order_id = sale_order.id

    def _confirm_existing_sale_order(self):
        """Confirma un pedido de venta existente si está en borrador."""
        if self.sale_order_id.state in ['draft', 'sent']:
            self.sale_order_id.action_confirm()

    def _prepare_sale_order_lines(self):
        """
        Prepara las líneas del pedido según las cantidades de entradas.
        
        Returns:
            list: Lista de tuplas (0, 0, {datos}) para crear sale.order.line
        """
        order_lines = []
        vip_product_id = self.env.ref('cinenvista.product_ticket_vip').id
        regular_product_id = self.env.ref('cinenvista.product_ticket_regular').id
        
        if self.qty_regular > 0:
            order_lines.append((0, 0, {
                'product_id': regular_product_id,
                'product_uom_qty': self.qty_regular,
            }))
        
        if self.qty_vip > 0:
            order_lines.append((0, 0, {
                'product_id': vip_product_id,
                'product_uom_qty': self.qty_vip,
            }))
        
        return order_lines

    # ============ VALIDACIONES ============
    @api.constrains('seat_ids', 'screening_id', 'state')
    def _check_seat_availability(self):
        """
        Valida la disponibilidad de asientos tanto individual
        como agregada para toda la sesión.
        """
        for record in self:
            if not record.screening_id or not record.screening_id.room_id or not record.seat_ids:
                continue
            
            capacity = record.screening_id.room_id.capacity or 0
            total_seats = len(record.seat_ids)
            
            # Validación: no exceder capacidad individual
            if total_seats > capacity:
                raise ValidationError(
                    _('No se pueden reservar más asientos de los que tiene '
                      'la sala (capacidad: %s).') % capacity
                )
            
            # Validación: no exceder capacidad total de la sesión
            if record.state == 'confirmed':
                domain = [
                    ('screening_id', '=', record.screening_id.id),
                    ('state', '=', 'confirmed')
                ]
                existing = self.search(domain).filtered(lambda r: r.id != record.id)
                total_confirmed = sum(existing.mapped('seat_qty')) or 0
                
                if (total_confirmed + total_seats) > capacity:
                    raise ValidationError(
                        _('No hay suficientes asientos disponibles para confirmar '
                          'la reserva.\nCapacidad: %s, ya confirmados: %s, '
                          'solicitados: %s') % (capacity, total_confirmed, total_seats)
                    )
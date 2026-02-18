from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CinenvistaTicketWizard(models.TransientModel):
    """
    Asistente transaccional para la venta rápida de entradas de cine.
    Permite seleccionar sesión, cliente, cantidad de entradas y sus butacas.
    Soporta dos flujos: compra normal con puntos de fidelización o canje de puntos.
    """
    _name = 'cinenvista.ticket.wizard'
    _description = 'Asistente de Venta Rápida de Entradas'

    # ============ CAMPOS ============
    # Relaciones
    screening_id = fields.Many2one(
        'cinenvista.screening',
        string='Sesión',
        required=True,
        help='Sesión de cine donde se venderán las entradas'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        help='Cliente comprador de las entradas'
    )
    
    # Cantidades
    qty_regular = fields.Integer(
        string='Entradas regulares',
        default=0,
        help='Cantidad de entradas regulares a vender'
    )
    qty_vip = fields.Integer(
        string='Entradas VIP',
        default=0,
        help='Cantidad de entradas VIP a vender'
    )
    
    # Opciones de compra
    redeem_points = fields.Boolean(
        string='¿Canjear puntos por entrada gratis?',
        help='Si está marcado, canjeará puntos de fidelización por entradas gratis'
    )
    
    # Información del cliente (lectura)
    available_points = fields.Integer(
        string='Puntos Disponibles',
        related='partner_id.loyalty_points',
        readonly=True,
        help='Puntos de fidelización disponibles del cliente'
    )
    
    # Sala relacionada (lectura)
    room_id = fields.Many2one(
        related='screening_id.room_id',
        string='Sala',
        store=False,
        help='Sala donde se proyectará la sesión'
    )
    
    # Butacas
    occupied_seat_ids = fields.Many2many(
        'cinenvista.seat',
        compute='_compute_occupied_seats',
        string='Butacas Ocupadas',
        help='Butacas ya reservadas/ocupadas en esta sesión'
    )
    selected_seat_ids = fields.Many2many(
        'cinenvista.seat',
        string='Seleccionar Butacas',
        domain="[('room_id', '=', room_id), ('id', 'not in', occupied_seat_ids)]",
        help='Butacas disponibles a seleccionar para la reserva'
    )


    # ============ MÉTODOS COMPUTADOS ============
    @api.depends('screening_id')
    def _compute_occupied_seats(self):
        """
        Calcula las butacas ocupadas/reservadas para la sesión actual.
        Solo considera reservas con estado confirmado.
        """
        for wizard in self:
            if wizard.screening_id:
                reservations = self.env['cinenvista.reservation'].search([
                    ('screening_id', '=', wizard.screening_id.id),
                    ('state', '=', 'confirmed')
                ])
                wizard.occupied_seat_ids = reservations.mapped('seat_ids')
            else:
                wizard.occupied_seat_ids = self.env['cinenvista.seat']

    # ============ MÉTODOS ACCIÓN ============
    def action_confirm_sale(self):
        """
        Valida los datos ingresados y delega al flujo correspondiente
        según si se canjean puntos o es una compra normal.
        """
        self.ensure_one()
        
        # Validar que haya butacas seleccionadas
        if not self.selected_seat_ids:
            raise ValidationError(_("Debe seleccionar al menos una butaca específica."))
        
        # Validar que la cantidad de entradas coincida con las butacas seleccionadas
        total_seats = len(self.selected_seat_ids)
        total_entries = self.qty_regular + self.qty_vip
        
        if total_entries != total_seats:
            raise ValidationError(
                _("La suma de entradas (%s) no coincide con las butacas seleccionadas (%s).")
                % (total_entries, total_seats)
            )

        # Delegar según el tipo de flujo
        if self.redeem_points:
            return self._process_redeem_points()
        else:
            return self._process_normal_sale()

    # ============ MÉTODOS DE PROCESAMIENTO ============
    def _process_redeem_points(self):
        """
        Procesa una venta canjeando puntos de fidelización.
        Canjea la máxima cantidad de entradas posibles respetando:
        - Prioridad a entradas VIP (200 puntos cada una)
        - Luego entradas Regular (100 puntos cada una)
        - Las entradas no canjeadas se pagan a precio normal
        """
        # Calcular entradas canjeables
        free_vip_qty, free_regular_qty, points_to_deduct = self._calculate_redeemable_entries()
        
        # Actualizar puntos del cliente
        self._update_customer_loyalty_points(points_to_deduct=points_to_deduct)
        
        # Crear pedido de venta
        sale_order = self._create_sale_order_with_entries(
            free_vip_qty=free_vip_qty,
            free_regular_qty=free_regular_qty,
            apply_discount=False
        )
        
        # Crear reserva
        self._create_reservation(sale_order)
        
        return {'type': 'ir.actions.act_window_close'}

    def _process_normal_sale(self):
        """
        Procesa una venta normal sin canjear puntos.
        El cliente gana 10 puntos por cada entrada comprada.
        Se aplica descuento según el nuevo nivel de membresía.
        """
        # Calcular puntos ganados y nuevo nivel
        total_entries = len(self.selected_seat_ids)
        self._update_customer_loyalty_points(points_earned=total_entries * 10)
        
        # Crear pedido de venta con descuento por nivel
        sale_order = self._create_sale_order_with_entries(
            apply_discount=True
        )
        
        # Crear reserva
        self._create_reservation(sale_order)
        
        return {'type': 'ir.actions.act_window_close'}

    # ============ MÉTODOS AUXILIARES (LOYALIDAD) ============
    def _calculate_redeemable_entries(self):
        """
        Calcula cuántas entradas se pueden canjear con los puntos disponibles.
        Retorna: (free_vip_qty, free_regular_qty, total_points_to_deduct)
        
        Utiliza esta prioridad:
        1. Canjea VIPs primero (200 puntos cada una)
        2. Con los puntos restantes, canjea Regulares (100 puntos cada una)
        """
        available_points = self.partner_id.loyalty_points
        free_vip_qty = 0
        free_regular_qty = 0
        points_to_deduct = 0

        # Canjear VIPs (prioridad)
        if self.qty_vip > 0:
            canjeables_vip = min(self.qty_vip, available_points // 200)
            free_vip_qty = canjeables_vip
            points_to_deduct += canjeables_vip * 200
            available_points -= points_to_deduct

        # Canjear Regulares con puntos restantes
        if self.qty_regular > 0 and available_points >= 100:
            canjeables_regular = min(self.qty_regular, available_points // 100)
            free_regular_qty = canjeables_regular
            points_to_deduct += canjeables_regular * 100

        # Validar que se haya canjeado al menos algo
        if points_to_deduct == 0:
            raise ValidationError(_("No tienes suficientes puntos para canjear entradas."))

        return free_vip_qty, free_regular_qty, points_to_deduct

    def _update_customer_loyalty_points(self, points_earned=0, points_to_deduct=0):
        """
        Actualiza los puntos de lealtad del cliente y su nivel de membresía.
        
        Args:
            points_earned (int): Puntos ganados por la compra
            points_to_deduct (int): Puntos deducidos por canje
        """
        new_total_points = self.partner_id.loyalty_points + points_earned - points_to_deduct
        new_level = self._calculate_member_level(new_total_points)
        
        self.partner_id.with_context(loyalty_already_processed=True).write({
            'loyalty_points': new_total_points,
            'member_level': new_level
        })

    def _calculate_member_level(self, points):
        """
        Calcula el nivel de membresía según los puntos totales.
        - Premium: > 1000 puntos
        - Silver: > 500 puntos
        - Standard: <= 500 puntos
        """
        if points > 1000:
            return 'premium'
        elif points > 500:
            return 'silver'
        else:
            return 'standard'

    # ============ MÉTODOS AUXILIARES (ÓRDENES) ============
    def _create_sale_order_with_entries(self, free_vip_qty=0, free_regular_qty=0, apply_discount=False):
        """
        Crea un pedido de venta con las líneas de entradas.
        
        Args:
            free_vip_qty (int): Cantidad de VIPs gratis
            free_regular_qty (int): Cantidad de Regulares gratis
            apply_discount (bool): Si aplicar descuento por nivel de membresía
            
        Returns:
            sale.order: El pedido de venta creado
        """
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
        })
        
        # Calcular descuento si se debe aplicar
        discount = 0.0
        if apply_discount:
            level = self._calculate_member_level(self.partner_id.loyalty_points)
            discount = self._get_discount_by_level(level)
        
        # Crear líneas de pedido
        order_lines = self._prepare_order_lines(free_vip_qty, free_regular_qty, discount)
        
        sale_order.write({'order_line': order_lines})
        sale_order.action_confirm()
        
        return sale_order

    def _prepare_order_lines(self, free_vip_qty=0, free_regular_qty=0, discount=0.0):
        """
        Prepara las líneas del pedido separando entradas gratis de pagadas.
        
        Returns:
            list: Lista de tuplas (0, 0, {datos_línea}) para crear sale.order.line
        """
        order_lines = []
        vip_product_id = self.env.ref('cinenvista.product_ticket_vip').id
        regular_product_id = self.env.ref('cinenvista.product_ticket_regular').id
        
        # Líneas de entradas regulares
        if self.qty_regular > 0:
            if free_regular_qty > 0:
                order_lines.append(self._create_line_data(
                    regular_product_id,
                    free_regular_qty,
                    price_unit=0.0
                ))
            
            if self.qty_regular > free_regular_qty:
                order_lines.append(self._create_line_data(
                    regular_product_id,
                    self.qty_regular - free_regular_qty,
                    discount=discount
                ))
        
        # Líneas de entradas VIP
        if self.qty_vip > 0:
            if free_vip_qty > 0:
                order_lines.append(self._create_line_data(
                    vip_product_id,
                    free_vip_qty,
                    price_unit=0.0
                ))
            
            if self.qty_vip > free_vip_qty:
                order_lines.append(self._create_line_data(
                    vip_product_id,
                    self.qty_vip - free_vip_qty,
                    discount=discount
                ))
        
        return order_lines

    def _create_line_data(self, product_id, qty, price_unit=None, discount=0.0):
        """
        Crea la estructura de datos para una línea de pedido.
        
        Args:
            product_id (int): ID del producto
            qty (int): Cantidad
            price_unit (float): Precio unitario (si es None, usa el del producto)
            discount (float): Porcentaje de descuento
            
        Returns:
            tuple: (0, 0, {datos})
        """
        line_data = {
            'product_id': product_id,
            'product_uom_qty': qty,
        }
        
        if price_unit is not None:
            line_data['price_unit'] = price_unit
        
        if discount > 0:
            line_data['discount'] = discount
        
        return (0, 0, line_data)

    def _get_discount_by_level(self, level):
        """
        Retorna el descuento según el nivel de membresía.
        - Premium: 20%
        - Silver: 10%
        - Standard: 0%
        """
        return {'premium': 20.0, 'silver': 10.0}.get(level, 0.0)

    # ============ MÉTODOS AUXILIARES (RESERVAS) ============
    def _create_reservation(self, sale_order):
        """
        Crea una reserva vinculada al pedido de venta.
        La presencia de sale_order_id indica que los puntos no deben
        procesarse nuevamente en el modelo de reserva.
        
        Args:
            sale_order (sale.order): Pedido de venta a vincular
        """
        self.env['cinenvista.reservation'].create({
            'screening_id': self.screening_id.id,
            'partner_id': self.partner_id.id,
            'qty_regular': self.qty_regular,
            'qty_vip': self.qty_vip,
            'seat_ids': [(6, 0, self.selected_seat_ids.ids)],
            'state': 'confirmed',
            'sale_order_id': sale_order.id,
        })
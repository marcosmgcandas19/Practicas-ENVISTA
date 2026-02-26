from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CinenvistaTicketWizardLine(models.TransientModel):
    """
    Modelo transitorio para representar las líneas de consumibles
    (snacks, bebidas, etc.) en el asistente de venta de entradas.
    """
    _name = 'cinenvista.ticket.wizard.line'
    _description = 'Líneas de Consumibles en Asistente de Entradas'

    # Relación con el wizard padre
    wizard_id = fields.Many2one(
        'cinenvista.ticket.wizard',
        string='Asistente',
        required=True,
        ondelete='cascade',
        help='Referencia al asistente de venta de entradas'
    )

    # Producto (consumibles y servicios)
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        domain=[('type', 'in', ['consu', 'service'])],
        help='Producto de consumición: snacks, bebidas, entradas, etc.'
    )

    # Cantidad
    quantity = fields.Integer(
        string='Cantidad',
        required=True,
        default=1,
        help='Cantidad de unidades del producto'
    )

    # Precio unitario (lectura, del producto)
    price_unit = fields.Float(
        string='Precio Unitario',
        related='product_id.list_price',
        readonly=True,
        help='Precio de venta del producto'
    )

    # Subtotal (computado)
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=False,
        help='Cantidad × Precio Unitario'
    )

    # Control de existencias
    stock_available = fields.Integer(
        string='Stock Disponible',
        compute='_compute_stock_available',
        help='Cantidad disponible en stock'
    )

    # ============ MÉTODOS COMPUTADOS ============
    @api.depends('product_id', 'quantity')
    def _compute_subtotal(self):
        """Calcula el subtotal de la línea"""
        for line in self:
            line.subtotal = line.quantity * line.product_id.list_price

    @api.depends('product_id')
    def _compute_stock_available(self):
        """Obtiene el stock disponible del producto"""
        for line in self:
            if line.product_id:
                # Busca el stock en el almacén del componente 'stock'
                try:
                    quant = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id),
                    ], limit=1)
                    line.stock_available = int(quant.available_quantity) if quant else 0
                except:
                    line.stock_available = 0
            else:
                line.stock_available = 0

    # ============ VALIDACIONES ============
    @api.constrains('quantity')
    def _check_quantity_positive(self):
        """Valida que la cantidad sea positiva"""
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    'La cantidad debe ser mayor a 0'
                )

    

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CinenvistPromotion(models.Model):
    _name = 'cinenvista.promotion'
    _description = 'Promociones y Campañas Comerciales'
    _order = 'name asc'

    name = fields.Char(
        string='Nombre de la Campaña',
        required=True,
        help='Nombre descriptivo de la campaña de promoción'
    )

    discount = fields.Float(
        string='Descuento (%)',
        required=True,
        default=0.0,
        help='Porcentaje de descuento a aplicar (de 0.0 a 100.0)'
    )

    active = fields.Boolean(
        default=True,
        help='Indica si la promoción se encuentra operativa'
    )

    product_ids = fields.Many2many(
        'product.product',
        relation='cinenvista_promotion_product_rel',
        column1='promotion_id',
        column2='product_id',
        domain=[('type', 'in', ['service', 'consu'])],
        string='Productos',
        help='Productos (servicios y consumibles) a los que se aplica esta promoción'
    )

    promo_type = fields.Selection(
        selection=[
            ('fixed', 'Día Fijo de la Semana'),
            ('range', 'Rango de Fechas'),
        ],
        string='Tipo de Promoción',
        required=True,
        default='fixed',
        help='Define la naturaleza de la vigencia de la promoción'
    )

    day_of_week = fields.Selection(
        selection=[
            ('0', 'Lunes'),
            ('1', 'Martes'),
            ('2', 'Miércoles'),
            ('3', 'Jueves'),
            ('4', 'Viernes'),
            ('5', 'Sábado'),
            ('6', 'Domingo'),
        ],
        string='Día de la Semana',
        help='Especifica el día de aplicación si el tipo es fijo'
    )

    date_start = fields.Date(
        string='Fecha de Inicio',
        help='Fecha en la que comienza la promoción (si el tipo es Rango de Fechas)'
    )

    date_end = fields.Date(
        string='Fecha de Finalización',
        help='Fecha en la que termina la promoción (si el tipo es Rango de Fechas)'
    )

    @api.constrains('discount')
    def _check_discount_range(self):
        """Valida que el descuento esté entre 0 y 100"""
        for record in self:
            if record.discount < 0.0 or record.discount > 100.0:
                raise ValidationError(
                    'El descuento debe estar entre 0.0 y 100.0'
                )

    @api.constrains('promo_type', 'day_of_week')
    def _check_day_of_week_for_fixed(self):
        for record in self:
            # En Odoo, los campos vacíos suelen devolver False, no None
            if record.promo_type == 'fixed' and not record.day_of_week:
                raise ValidationError(
                    'Debe especificar un día de la semana para promociones de tipo fijo'
            )

    @api.constrains('promo_type', 'date_start', 'date_end')
    def _check_dates_for_range(self):
        """Valida que si el tipo es 'range', las fechas estén definidas y sean válidas"""
        for record in self:
            if record.promo_type == 'range':
                if not record.date_start or not record.date_end:
                    raise ValidationError(
                        'Debe especificar fecha de inicio y finalización para promociones de rango'
                    )
                if record.date_start > record.date_end:
                    raise ValidationError(
                        'La fecha de inicio no puede ser posterior a la fecha de finalización'
                    )

    @api.onchange('promo_type')
    def _onchange_promo_type(self):
        """Limpia campos no aplicables cuando cambia el tipo de promoción"""
        if self.promo_type == 'fixed':
            self.date_start = None
            self.date_end = None
        elif self.promo_type == 'range':
            self.day_of_week = None

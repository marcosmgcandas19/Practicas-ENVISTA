# -*- coding: utf-8 -*-
{
    'name': "Toji Store",

    'summary': "Módulo para gestionar libros en la tienda",

    'description': """
Módulo que extiende el modelo de productos para crear un sistema de gestión de libros.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Sales',
    'version': '0.1',

    'depends': [
        'base',
        'product',
    ],

    'data': [

        'security/ir.model.access.csv',
        'views/toji_product.xml',
        'views/menus.xml', 

    ],

    'demo': [
    ],

    'installable': True,
    'application': False,
}


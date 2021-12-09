# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Position By Location | Stock By Location | Stocks By Location',
    'version': '1.0',
    'category': 'Warehouse',
    'sequence': 1,
    'author': 'Xetechs, S.A.',
    'support': 'Luis Aquino -> laquino@xetechs.com',
    'website': 'https://www.xetechs.com',
    'license': 'AGPL-3',
    'description': """
        Product Stocks By locations,
    """,
    'depends': ['base', 'sale', 'stock'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/stock_positioning_lines_view.xml',
        'report/stock_positioning_report_view.xml',
    ],
    'demo': [],
    'test': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

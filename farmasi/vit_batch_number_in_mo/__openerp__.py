# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Batch Number in Manufacturing Orders',
    'description': """
*Tambah Batch Number di Manufakturing Orders
""",
    'version': '0.1',
    'depends': ['base','mrp','mrp','mrp_operations'],
    'author': 'vitraining.com',
    'category': 'mrp',
    'url': 'http://www.vitraining.com/',
    'data': [ 
        
        'view_batch_number.xml',
        'view_mrp.xml',
        'view_product_date.xml'
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
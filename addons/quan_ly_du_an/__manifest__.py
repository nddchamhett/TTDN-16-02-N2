# -*- coding: utf-8 -*-
{
    'name': "quan_ly_du_an",

    'summary': """
        Quản lý dự án, dùng chung cho các module quản lý công việc và nhân sự""",

    'description': """
        Module quản lý dự án tách riêng, liên kết với:
        - Module quản lý công việc (quan_ly_cong_viec)
        - Module nhân sự (nhan_su)
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Project',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'nhan_su'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/du_an_view.xml',
        'views/tai_nguyen_view.xml',
        'views/menu.xml',
    ],

    'demo': [],
}



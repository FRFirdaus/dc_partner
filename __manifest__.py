{
    'name': "dc_partner",
    'summary': """
         Dewi coryati partner customize
         """,

    'description': """
         Dewi coryati partner customize
    """,
    'author': "Rehan | Fahmi Roihanul Firdaus",
    'website': "https://www.frayhands.com",
    'category': 'Uncategorized',
    "external_dependencies": {"python": ["xlrd"], "bin": []},
    'version': '0.1',
    'depends': [
        'base',
        'mail'
    ],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        # 'views/partner_views.xml',
        'views/dc_partner_views.xml',
        'wizard/import_partner_wizard_views.xml',
        'views/menu_views.xml'
    ]
}
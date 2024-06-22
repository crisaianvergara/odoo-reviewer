{
  'name': 'My Library',
  'summary': 'Manage books and easily',
  'description': '''Manage Library''',
  'author': 'Cris-aian Vergara',
  'website': 'http://crisaianvergara.com',
  'category': 'Tools',
  'version': '13.0.1',
  'depends': ['base', 'contacts'],
  'data': [
    'security/groups.xml',
    'security/ir.model.access.csv',

    'views/library_book.xml',
    'views/library_book_categ.xml',
    'views/library_book_rent.xml',

    'wizard/library_book_rent_wizard.xml',
    'wizard/library_book_return_wizard.xml',

    'data/data.xml',
  ],
  'demo': [
    'data/demo.xml',
  ],
  'sequence': -97,
  'application': True,
  'installable': True,
  'license': 'LGPL-3',
}
from odoo import api, fields, models


class LibraryBookCopy(models.Model):
  _name = "library.book.copy"
  _inherit = "library.book"
  _description = "Library Book Copy"

  
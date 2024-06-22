import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

class LibraryRentWizard(models.TransientModel):
  _name = 'library.rent.wizard'

  borrower_id = fields.Many2one('res.partner', string='Borrower')
  book_ids = fields.Many2many('library.book', string='Books')

  def add_book_rents(self):
    _logger.info("----- Function: add_book_rents -----")
    
    rentModel = self.env['library.book.rent']

    for wiz in self:
      for book in wiz.book_ids:
        rentModel.create({
          'borrower_id': wiz.borrower_id.id,
          'book_id': book.id,
        })
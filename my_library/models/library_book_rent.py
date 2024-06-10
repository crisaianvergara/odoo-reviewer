import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LibraryBookRent(models.Model):
  _name = 'library.book.rent'
  _description = 'Library Book Rent'

  book_id = fields.Many2one('library.book', 'Book', required=True)
  borrower_id = fields.Many2one('res.partner', 'Borrower', required=True)
  state = fields.Selection(
    [
      ('ongoing', 'Ongoing'),
      ('returned', 'Returned'),
    ],
    'State',
    default='ongoing',
    required=True
  )
  rent_date = fields.Date(default=fields.Date.today())
  return_date = fields.Date()

  @api.model
  def create(self, vals):
    _logger.info("----- Function: create -----")

    book_rec = self.env['library.book'].browse(vals['book_id']) # returns record set from for given id
    book_rec.make_borrowed()

    return super(LibraryBookRent, self).create(vals)
  
  def book_return(self):
    _logger.info("----- Function: book_return -----")

    self.ensure_one()
    self.book_id.make_available()
    self.write({
      'state': 'returned',
      'return_date': fields.Date.today(),
    })




  
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class LibraryReturnWizard(models.TransientModel):
  _name = 'library.return.wizard'

  borrower_id = fields.Many2one('res.partner', string='Member')
  book_ids = fields.Many2many('library.book', string='Books')

  def book_returns(self):
    _logger.info("----- Function: book_returns -----")
    
    loanModel = self.env['library.book.rent']

    for rec in self:
      loans = loanModel.search(
        [
          ('state', '=', 'ongoing'),
          ('book_id', 'in', rec.book_ids.ids),
          ('borrower_id', '=', rec.borrower_id.id),
        ]
      )
      for loan in loans:
        loan.book_return()

  @api.onchange("borrower_id")
  def onchange_member(self):
    _logger.info("----- Function: onchange_member -----")

    rentModel = self.env['library.book.rent']
    books_on_rent = rentModel.search(
      [
        ('state', '=', 'ongoing'),
        ('borrower_id', '=', self.borrower_id.id),
      ]
    )
    self.book_ids = books_on_rent.mapped('book_id')
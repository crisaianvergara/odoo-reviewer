from datetime import timedelta

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class LibraryBook(models.Model):
  _inherit = "library.book"

  date_return = fields.Date("Date to return")

  def make_borrowed(self):
    _logger.info("----- Function: make_borrowed (extended business logic) -----")

    day_to_borrow = self.category_id.max_borrow_days or 10
    self.date_return = fields.Date.today() + timedelta(days=day_to_borrow)

    return super(LibraryBook, self).make_borrowed()
  
  def make_available(self):
    _logger.info("----- Function: make_available (extended business logic) -----")

    self.date_return = False
    return super(LibraryBook, self).make_available()


class LibraryBookCategory(models.Model):
  _inherit = "library.book.category"

  max_borrow_days = fields.Integer(
    "Maximum borrow days",
    help="For how many days book can be borrowed",
    default=10,
  )
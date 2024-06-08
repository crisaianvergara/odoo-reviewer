from odoo import fields, models, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class BookCategory(models.Model):
  _name = "library.book.category"
  _description = "Library Book Category"

  _parent_store = True
  _parent_name = "parent_id" # optional field is "parent_id"
  
  name = fields.Char("Category")
  description = fields.Text("Description")
  parent_id = fields.Many2one(
    "library.book.category",
    string="Parent Category",
    ondelete="restrict",
    index=True,
  )
  child_ids = fields.One2many(
    "library.book.category",
    "parent_id",
    string="Child Categories",
  )
  parent_path = fields.Char(index=True)

  @api.constrains("parent_id")
  def _check_hierarchy(self):
    _logger.info("----- Function: _check_hierarchy -----")

    if not self._check_recursion():
      raise models.ValidationError(
        "Error! You cannot create recursive categories."
      )
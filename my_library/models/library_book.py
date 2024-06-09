from datetime import timedelta

from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class BaseArchive(models.AbstractModel):
  _name = "base.archive"
  _description = "Base Archive"
  
  active = fields.Boolean(default=True)

  def do_archive(self):
    for record in self:
        record.active = not record.active

        
class LibraryBook(models.Model):
  _name = 'library.book'
  _inherit = ["base.archive"]

  _description = 'Library Book'

  _order = "date_release desc, name"
  _rec_name = "short_name"

  _sql_constraints = [
    ("name_uniq", "UNIQUE (name)", "Book title must be unique."),
    ("positive_page", "CHECK(pages>0)", "No. of pages must be positive."),
  ]
  
  name = fields.Char('Title', required=True)
  short_name = fields.Char('Short Title', translate=True, index=True)
  notes = fields.Text('Internal Notes')
  state = fields.Selection(
    [
      ('draft', 'Unavailable'),
      ('available', 'Available'),
      ('borrowed', 'Borrowed'),
      ('lost', 'Lost'),
    ], 'State', default='draft'
  )
  description = fields.Html('Description', sanitize=True, strip_style=False)
  cover = fields.Binary('Book Cover')
  out_of_print = fields.Boolean('Out of Print?')
  date_release = fields.Date('Release Date')
  date_updated = fields.Datetime('Last Updated')
  pages = fields.Integer(
    'Number of Pages',
    groups='base.group_user',
    states={'lost': [('readonly', True)]},
    help='Total book page count',
    company_dependent=False
  )
  reader_rating = fields.Float('Reader Average Rating', digits=(14, 4))
  author_ids = fields.Many2many('res.partner', string='Authors')
  cost_price = fields.Float("Book Cost", digits="Book Price")
  currency_id = fields.Many2one('res.currency', string="Currency")
  retail_price = fields.Monetary("Retail Price",
    # optional: currency_field="currency_id"
  )
  publisher_id = fields.Many2one(
    "res.partner", string="Publisher",
    # optional: 
    ondelete="set null",
    context={},
    domain=[],
  )
  publisher_city = fields.Char(
    "Publisher City",
    related="publisher_id.city",
    readonly=True,
  )
  category_id = fields.Many2one("library.book.category")
  age_days = fields.Float(
    string="Days Since Release",
    compute="_compute_age",
    inverse="_inverse_age",
    search="_search_age",
    store=False, # optional
    compute_sudo=True, #optional
  )
  ref_doc_id = fields.Reference(
    selection="_referencable_models",
    string="Reference Document"
  )
  manager_remarks = fields.Text("Manager Remarks")
  isbn = fields.Char("ISBN")
  old_edition = fields.Many2one("library.book", string="Old Edition")


  @api.model
  def create(self, values):
    """Extend the create() method"""
    _logger.info("----- Function: create() (Extend the create() method) -----")
    
    if not self.user_has_groups("my_library.group_librarian"):
      if "manager_remarks" in values:
        raise UserError("You are not allowed to modify " "manager_remarks")
      
    return super(LibraryBook, self).create(values)
  
  def write(self, values):
    """Extend the write() method"""
    _logger.info("----- Function: write() (Extend the write() method) -----")
    
    if not self.user_has_groups("my_library.group_librarian"):
      if "manager_remarks" in values:
        raise UserError("You are not allowed to modify " "manager_remarks")
      
    return super(LibraryBook, self).write(values)

  def sort_books(self):
    """Sorting record set"""
    _logger.info("----- Function: sort_books -----")

    all_books = self.search([])
    _logger.info(f"----- Type of all_books: {type(all_books)} -----")

    books_sorted = self.sort_books_by_date(all_books)
    _logger.info(f"----- Books before sorting: {all_books} -----")
    _logger.info(f"----- Books after sorting: {books_sorted} -----")

  @api.model
  def sort_books_by_date(self, books):
    _logger.info("----- Function: sort_books_by_date -----")
    _logger.info(f"----- Books: {books} -----")
    _logger.info(f"----- Type of books: {type(books)} -----")

    return books.sorted(key="date_release")

  def mapped_books(self):
    """Traversing record set"""
    _logger.info("----- Function: mapped_books -----")

    all_books = self.search([])
    book_authors = self.get_author_names(all_books)
    
    _logger.info(f"----- Book Authors: {book_authors} -----")

  @api.model
  def get_author_names(self, books):
    _logger.info("----- Function: get_author_names -----")
    _logger.info(f"----- Books: {books} -----")

    return books.mapped("author_ids.name")

  def filter_books(self):
    _logger.info("----- Function: filter_books -----")

    all_books = self.search([])
    filtered_books = self.books_with_multiple_authors(all_books)
    _logger.info(f"----- Filtered: {filtered_books} -----")
    
  @api.model
  def books_with_multiple_authors(self, all_books):
    _logger.info("----- Function: books_with_multiple_authors -----")

    def predicate(book):
      _logger.info("----- Function: predicate -----")
      _logger.info(f"----- book: {book} -----")
      
      if len(book.author_ids) > 1:
        return True
  
    return all_books.filtered(predicate)

  def find_book(self):
    _logger.info("----- Function: find_book -----")

    domain = [
      "|",
        "&", ("name", "ilike", "Book Name"),
             ("category_id.name", "ilike", "Category Name"),
        "&", ("name", "ilike", "Book Name 2"),
             ("category_id.name", "ilike", "Category Name 2"),
    ]

    books = self.search(domain)
    _logger.info(f"----- Books: {books} -----")

    return True

  def find_partner(self):
    _logger.info("----- Function: find_partner -----")

    PartnerObj = self.env["res.partner"]
    domain= [
      "&", ("name", "ilike", "Parth Gajjar"),
           ("company_id.name", "=", "Odoo"),
    ]

    partner = PartnerObj.search(domain)

  def change_release_date(self):
    _logger.info("----- Function: change_release_date -----")

    self.ensure_one()
    self.date_release = fields.Date.today()

  # def change_update_date(self):
  # _logger.info("----- Function: change_update_date -----")

  #   self.ensure_one()
  #   self.update({
  #     "date_release": fields.Datetime.now(),
  #     "another_field": "value",
  #   })

  def create_categories(self):
    _logger.info("----- Function: create_categories -----")

    categ1 = {
      "name": "Child category 1",
      "description": "Description for child 1",
    }

    categ2 = {
      "name": "Child category 2",
      "description": "Description for child 2",
    }

    parent_category_val = {
      "name": "Parent category",
      "description": "Description for parent category",
      "child_ids": [
        (0, 0, categ1),
        (0, 0, categ2),
      ],
    }

    # Total 3 records (1 parent and 2 child) will be craeted in library.book.category model
    record = self.env["library.book.category"].create(parent_category_val)
    
    return True

  def log_all_library_members(self):
    _logger.info("----- Function: log_all_library_members -----")

    # This is an empty recordset of model library.member
    library_member_model = self.env["library.member"]
    all_members = library_member_model.search([])

    _logger.info(f"ALL MEMBERS: {all_members}")
    
    return True

  @api.model
  def is_allowed_transition(self, old_state, new_state):
    _logger.info("----- Function: is_allowed_transition -----")

    allowed = [
      ('draft', 'available'),
      ('available', 'borrowed'),
      ('borrowed', 'available'),
      ('available', 'lost'),
      ('borrowed', 'lost'),
      ('lost', 'available'),
    ]

    return (old_state, new_state) in allowed
  
  def change_state(self, new_state):
    _logger.info("----- Function: change_state -----")

    for book in self:
      if book.is_allowed_transition(book.state, new_state):
        book.state = new_state
      else:
        msg = _("Moving from %s to %s is not allowed") % (book.state, new_state)
        raise UserError(msg)
  
  def make_available(self):
    _logger.info("----- Function: make_available -----")

    self.change_state("available")

  def make_borrowed(self):
    _logger.info("----- Function: make_borrowed -----")

    self.change_state("borrowed")

  def make_lost(self):
    _logger.info("----- Function: make_lost -----")

    self.change_state("lost")

  @api.model
  def _referencable_models(self):
    _logger.info("----- Function: _referencable_models -----")

    models = self.env["ir.model"].search([
      ("field_id.name", "=", "message_ids")
    ])

    return [(x.model, x.name,) for x in models]
  
  @api.depends("date_release")
  def _compute_age(self):
    _logger.info("----- Function: _compute_age -----")

    today = fields.Date.today()

    for book in self:
      if book.date_release:
        delta = today - book.date_release
        book.age_days = delta.days
      else:
        book.age_days = 0
  
  def _inverse_age(self):
    """
      This reverse method of _compute_age. Used to make age_days field editable
      It is optional if you don't want to make compute field editable then you can remove this
    """
    _logger.info("----- Function: _inverse_age -----")

    today = fields.Date.today()

    for book in self.filtered("date_release"):
      d = today - timedelta(days=book.age_days)
      book.date_release = d

  def _search_age(self, operator, value):
    """
      This used to enable search on compute fields
      It is optional if you don't want to make enable search then you can remove this
    """
    _logger.info("----- Function: _search_age -----")

    today = fields.Date.today()
    value_days = timedelta(days=value)
    value_date = today - value_days
    #convert the operator:
    # book with age > value have a date < value_date
    operator_map = {
      "<": "<", ">=": "<=",
      "<": ">", "<=": ">=",
    }
    new_op = operator_map.get(operator, operator)

    return [("date_release", new_op, value_date)]

  @api.constrains("date_release")
  def _check_release_date(self):
    _logger.info("----- Function: _check_release_date -----")

    for record in self:
      if record.date_release and record.date_release > fields.Date.today():
        raise models.ValidationError("release date must be in the past")

  # def name_get(self):
  #   _logger.info("----- Function: name_get -----")

  #   result = []

  #   for record in self:
  #     rec_name = "%s (%s)" % (record.name, record.date_release)
  #     result.append((record.id, rec_name))
    
  #   return result
  
  def name_get(self):
    _logger.info("----- Function: name_get -----")
    
    result = []

    for book in self:
      authors = book.author_ids.mapped("name")
      name = "%s (%s)" % (book.name, ", " .join(authors))
      result.append((book.id, name))

    return result

  @api.model
  def _name_search(self, name="", args=None, operator="ilike", limit=100, name_get_uid=None):
    _logger.info("----- Function: _name_search -----")

    args = [] if args is None else args.copy()
    
    if not (name == "" and operator == "ilike"):
      args += [
        "|", "|",
        ("name", operator, name),
        ("isbn", operator, name),
        ("author_ids.name", operator, name)
      ]

    return super(LibraryBook, self)._name_search(
      name=name, args=args,
      operator=operator,
      limit=limit,
      name_get_uid=name_get_uid,
    )

  # Fetching data in groups using read_group()
  def grouped_data(self):
    _logger.info("----- Function: grouped_data -----")

    data = self._get_average_cost()

    _logger.info(f"----- Data: {data} -----")

  @api.model
  def _get_average_cost(self):
    _logger.info("----- Function: _get_average_cost -----")

    grouped_result = self.read_group(
      [('cost_price', '!=', False)], # Domain
      ['category_id', 'cost_price:avg'], # Fields to access
      ['category_id'] # group_by
    )

    _logger.info(f"----- Grouped Result: {grouped_result} -----")

    return grouped_result

  # Invoking functions from XML files
  @api.model
  def _update_book_price(self):
    _logger.info("----- Function: _update_book_price -----")

    all_books = self.search([])

    for book in all_books:
      book.cost_price += 10


class ResPartner(models.Model):
  _inherit = "res.partner"

  _order_name = "name"

  authored_book_ids = fields.Many2many(
    "library.book",
    string="Authored Books"
  )
  count_books = fields.Integer(
    "Number of Authored Books",
    compute="_compute_count_books",
  )
  published_books_ids = fields.One2many(
    "library.book", "publisher_id",
    string="Published Books"
  )
  authored_book_ids = fields.Many2many(
    "library.book",
    string="Authored Books",
    # relation="library_book_res_partner_rel",
    # optional
  )

  @api.depends("authored_book_ids")
  def _compute_count_books(self):
    _logger.info("----- Function: _compute_count_books -----")

    for r in self:
      r.count_books = len(r.authored_book_ids)


class LibraryMember(models.Model):
  _name = "library.member"
  # _inherits = {"res.partner": "partner_id"} # Delegation first method
  _description = "Library Member"

  partner_id = fields.Many2one(
    "res.partner",
    ondelete="cascade",
    delegate=True, # Delegation second method
  )
  date_start = fields.Date("Member Since")
  date_end = fields.Date("Termination Date")
  member_number = fields.Char()
  date_of_birth = fields.Date("Date of Birth")
import time

from odoo import models

import logging
_logger = logging.getLogger(__name__)

class RestPartner(models.Model):
  _inherit = 'res.partner'

  def _auto_create_contacts(self):
    'Auto create contacts'
    _logger.info('----- Function: _auto_create_contacts -----')

    for _ in range(10):
      self.with_delay()._create_contact(10)
    

  def _create_contact(self, records):
    'Auto create contact'
    _logger.info('----- Function: _create_contact -----')

    for _ in range(records):
      data = {
        'name': 'Contact_',
        'function': 'Farmer',
        'email': 'Contact_@gmail.com',
        'phone': '1234567890',
        'mobile': '1234567890',
        'is_company': False,
        'website': 'http://crisaianvergara.com',
      }
      
      try:
        self.create(data)
        _logger.info('----- Created contact... -----')
      except Exception as e:
        _logger.info(f'----- Error creating contact...: {e} -----')

      time.sleep(20)


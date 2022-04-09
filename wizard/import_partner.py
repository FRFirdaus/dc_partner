# -*- coding: utf-8 -*-
import base64
from datetime import datetime
from odoo import fields, models, _
from odoo.exceptions import UserError

try:
    import xlrd
except ImportError:
    xlrd = None

class ImportPartnerPIPKIP(models.TransientModel):
    _name = 'import.partner.pip.kip'
    _description = 'Import partner PIP/KIP'

    file_import = fields.Binary(string="File ( .xls )")
    filename = fields.Char('Filename')
    info = fields.Text('Info')
    partner_program = fields.Selection([
        ('PIP', "Program PIP"),
        ('KIP', "Program KIP")],
        required=True
    )

    def action_import_partner(self):
        print("miawww")

    def action_export_partner(self):
        # Function to generate csv template example..
        attachment = self.env['ir.attachment'].sudo().search([('name','=','Bulk Import Partner PIP KIP (Example).xlsx')], limit=1)
        if not attachment:
            raise UserError('Example document not found, please upload on attachment first !')
        else:
            return {
                'name': 'Download Excel',
                'type': 'ir.actions.act_url',
                'url': "web/content/ir.attachment/" + str(attachment.id) + "/datas/" + attachment.name + "?download=true",
                'target': 'download',
            }
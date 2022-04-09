# -*- coding: utf-8 -*-
import base64
from datetime import datetime
from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError

try:
    import xlrd
except ImportError:
    xlrd = None

class ImportPartnerPIPKIP(models.TransientModel):
    _name = 'import.partner.pip.kip'
    _description = 'Import partner PIP/KIP'

    file_import = fields.Binary(string="File Excel ( .xls )")
    filename = fields.Char('Filename')
    info = fields.Text('Info')
    partner_program = fields.Selection([
        ('PIP', "Program PIP"),
        ('KIP', "Program KIP")],
        required=True
    )

    def action_import_partner(self):
        if not self.file_import:
            raise UserError('Please choose file to be upload !')  
        try:
            xl_workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.file_import))
        except:
            raise UserError('Incorrect File Format!')

        self.info = ""
        xl_sheet = xl_workbook.sheet_by_index(0)
        for row in range(1, xl_sheet.nrows):
            info, values = self.row_validation(xl_sheet, row)
            if info:
                self.info = '</br>'.join(info)
            else:
                dc_partner_id = self.env['dc.partner'].search([('nik_number', '=', values['nik_number'])])
                if not dc_partner_id:
                    create_dc_partner = self.env['dc.partner'].create(values)
                else:
                    update_dc_partner = dc_partner_id.write(values)
        if self.info:
            raise ValidationError(_("Error ketika import data"))

        domain = [('pip_program','=',True)] if self.partner_program == "PIP" else [('kip_program','=',True)]
        return {
            'name': _('DC %s Partner' % (self.partner_program)),
            'view_mode': 'kanban,tree,form,graph',
            'res_model': 'dc.partner',
            'domain': domain,
            'type': 'ir.actions.act_window'
        }

    def row_validation(self, xl_sheet, row):
        # Function to checking row content
        village_id = False
        city_id = False
        province_id = False
        country_id = False
        info = []
        birth_date = self.date_format(xl_sheet.cell(row, 6).value.strip())
        payment_vals = False
        if not birth_date:
            raise UserError('Incorrect data format on row %s, should be YYYY-MM-DD' % (row+1))

        for x in range(15):
            if not xl_sheet.cell(row, x).value:
                raise UserError('Missing value on label column %s on row %s, this is mandatory column' % (x, row+1))
        
        if xl_sheet.cell(row, 7).value:
            village = self._find_village(xl_sheet.cell(row, 7).value)
            if village:
                village_id = village
            else:
                info.append("Desa %s tidak ditemukan dalam baris %s" % (xl_sheet.cell(row, 7).value, row+1))
        if xl_sheet.cell(row, 8).value:
            city = self._find_city(xl_sheet.cell(row, 8).value)
            if city:
                city_id = city
            else:
                info.append("Kota %s tidak ditemukan dalam baris %s" % (xl_sheet.cell(row, 8).value, row+1))
        if xl_sheet.cell(row, 9).value:
            province = self._find_province(xl_sheet.cell(row, 9).value)
            if province:
                province_id = province
            else:
                info.append("Provinsi %s tidak ditemukan dalam baris %s" % (xl_sheet.cell(row, 9).value, row+1))
        if xl_sheet.cell(row, 10).value:
            country = self._find_country(xl_sheet.cell(row, 10).value)
            if country:
                country_id = country
            else:
                info.append("Negara %s tidak ditemukan dalam baris %s" % (xl_sheet.cell(row, 10).value, row+1))

        values = {
            'name': xl_sheet.cell(row, 0).value,
            'nik_number': xl_sheet.cell(row,1).value,
            'address': xl_sheet.cell(row,2).value,
            'gender': xl_sheet.cell(row,3).value,
            'religion': xl_sheet.cell(row,4).value,
            'birth_place': xl_sheet.cell(row,5).value,
            'birth_date': birth_date,
            'village_id': village_id,
            'city_id': city_id,
            'province_id': province_id,
            'country_id': country_id,
            'email': xl_sheet.cell(row,11).value,
            'mobile': xl_sheet.cell(row,12).value
        }

        if xl_sheet.cell(row, 13).value and xl_sheet.cell(row, 14).value:
            program = self._find_program(self.partner_program, xl_sheet.cell(row, 13).value, xl_sheet.cell(row, 14).value)
            if program:
                if self.partner_program == "PIP":
                    values['pip_program_ids'] = [(4, program)]
                    values['pip_program'] = True
                else:
                    values['kip_program_ids'] = [(4, program)]
                    values['kip_program'] = True
            else:
                info.append("%s Program %s dengan periode %s tidak ditemukan dalam baris %s" % (self.partner_program, xl_sheet.cell(row, 13).value, xl_sheet.cell(row, 14).value, row+1))
        
        return info, values

    def date_format(self, date):
        # Function to check dateformat
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
            date = date.strftime('%Y-%m-%d')
            return date
        except:
            return False

    def _find_village(self, name):
        village_id = self.env['dc.partner.village'].search([('name', '=', name)],limit=1)
        if village_id:
            return village_id.id
        else:
            return False
    
    def _find_city(self, name):
        city_id = self.env['dc.partner.city'].search([('name', '=', name)],limit=1)
        if city_id:
            return city_id.id
        else:
            return False
    
    def _find_province(self, name):
        province_id = self.env['res.country.state'].search([('name', '=', name)],limit=1)
        if province_id:
            return province_id.id
        else:
            return False
    
    def _find_country(self, name):
        country_id = self.env['res.country'].search([('name', '=', name)],limit=1)
        if country_id:
            return country_id.id
        else:
            return False

    def _find_program(self, program_type, name, periode):
        program_id = False
        model_name = 'dc.pip.program' if program_type == 'PIP' else 'dc.kip.program'
        program_id = self.env[model_name].search([('name', '=', name), ('periode', '=', str(periode))], limit=1)
        if program_id:
            return program_id.id
        else:
            create_program_id = self.env[model_name].create({
                "name": name,
                "periode": str(periode)
            })

            return create_program_id.id

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
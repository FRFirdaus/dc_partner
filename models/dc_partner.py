from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class DCPartnerClass(models.Model):
    _name = 'dc.partner'
    _description = 'Partner of Dewi Coryati PIP and KIP'
    _inherit = ['mail.thread']
    _order = 'name'
    _sql_constraints = [
        ('unique_number_nik', 'unique(nik_number)', 'Nomor KTP sudah terdaftar, Partner harus memilik nomor ktp yang unik (tidak boleh duplicate)')
    ]
    
    image = fields.Binary()
    pip_program = fields.Boolean()
    kip_program = fields.Boolean()
    name = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    birth_place = fields.Char(
        track_visibility='onchange',
        required=True
    )
    birth_date = fields.Date(
        track_visibility='onchange',
        required=True
    )
    mobile = fields.Char(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    address = fields.Text(track_visibility='onchange')
    village_id = fields.Many2one('dc.partner.village', required=True, track_visibility='onchange')
    city_id = fields.Many2one('dc.partner.city', required=True, track_visibility='onchange')
    province_id = fields.Many2one('res.country.state', required=True, track_visibility='onchange')
    country_id = fields.Many2one('res.country', required=True, track_visibility='onchange')
    religion = fields.Selection([
        ('Islam', 'Islam'),
        ('Kristen Katolik', 'Kristen Katolik'),
        ('Kristen Protestan', 'Kristen Protestan'),
        ('Hindu', 'Hindu'),
        ('Buddha', 'Buddha'),
        ('Kong Hu Cu', 'Kong Hu Cu')],
        default='islam',
        sting='Agama',
        required=True
    )
    gender = fields.Selection([
        ('Pria', 'Pria'),
        ('Wanita', 'Wanita')],
        default='pria',
        required=True
    )
    nik_number = fields.Char(required=True)
    active = fields.Boolean(default=True)

    follower_ids = fields.One2many(
        'dc.partner',
        'inviter_id',
        track_visibility='onchange'
    )

    inviter_id = fields.Many2one('dc.partner', index=True)

    kip_program_ids = fields.Many2many('dc.kip.program')
    pip_program_ids = fields.Many2many('dc.pip.program')
    konstituen_id = fields.Many2one('dc.partner.konstituen')

    @api.constrains('kip_program', 'pip_program', 'kip_program_ids', 'kip_program_ids')
    def _constrains_kip_pip_program(self):
        for rec in self:
            if not rec.inviter_id and (not rec.kip_program and not rec.pip_program):
                raise ValidationError(_("Partner harus dalam penerima PIP/KIP Program"))

            # rec.kip_program = True if rec.kip_program_ids else False
            # rec.pip_program = True if rec.pip_program_ids else False

    def name_get(self):
        result = []
        for rec in self:
            if rec.inviter_id:
                result.append((rec.id, "%s, %s" % (rec.inviter_id.name, rec.name)))
            else:
                result.append((rec.id, rec.name))

        return result

class DCPIPProgram(models.Model):
    _name = 'dc.pip.program'
    _sql_constraints = [
        ('unique_name_periode', 'unique(name, periode)', 'Nama program PIP dengan periode sudah terdaftar, data PIP program harus memilik nama dan periode unik (tidak boleh duplicate)')
    ]

    name = fields.Char(required=True)
    periode = fields.Char(required=True)

    def name_get(self):
        result = []
        for rec in self:
           result.append((rec.id, "%s (%s)" % (rec.name, rec.periode)))

        return result

class DCKIPProgram(models.Model):
    _name = 'dc.kip.program'
    _sql_constraints = [
        ('unique_name_periode', 'unique(name, periode)', 'Nama program KIP dengan periode sudah terdaftar, data KIP program harus memilik nama dan periode unik (tidak boleh duplicate)')
    ]

    name = fields.Char(required=True)
    periode = fields.Char(required=True)
    pic = fields.Char()

    def name_get(self):
        result = []
        for rec in self:
           result.append((rec.id, "%s (%s)" % (rec.name, rec.periode)))

        return result

class DCPartnerVillage(models.Model):
    _name = 'dc.partner.village'

    name = fields.Char(required=True)
    city_id = fields.Many2one('dc.partner.city')
    pic = fields.Char()

    def name_get(self):
        result = []
        for rec in self:
            if rec.city_id:
                values = "%s/%s" % (rec.city_id.name, rec.name)
                if rec.city_id.state_id:
                    values = "%s/%s" % (rec.city_id.state_id.name, values)
                result.append((rec.id, values))
            else:
                result.append((rec.id, rec.name))

        return result

class DCPartnerCity(models.Model):
    _name = 'dc.partner.city'

    name = fields.Char(required=True)
    state_id = fields.Many2one('res.country.state')

    def name_get(self):
        result = []
        for rec in self:
            if rec.state_id:
                result.append((rec.id, "%s/%s" % (rec.state_id.name, rec.name)))
            else:
                result.append((rec.id, rec.name))

        return result

class DCKonstituen(models.Model):
    _name = 'dc.partner.konstituen'

    name = fields.Char()
    pic = fields.Char()
    city_id = fields.Many2one('dc.partner.city')
    partner_ids = fields.One2many('dc.partner', 'konstituen_id')
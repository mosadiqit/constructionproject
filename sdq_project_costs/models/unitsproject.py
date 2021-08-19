# import dp as dp
from odoo import models, fields, api,_


class projectUnits(models.Model):
    _name = 'project.units'
    _description = 'project units'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # ref = fields.Char(string='Référence', track_visibility="always")
    project_description = fields.Text(string='Déscription', required=False, track_visibility="always")
    location = fields.Char(string='Adresse', track_visibility="always")
    city = fields.Selection([
        ('agadir', 'Agadir'),
        ('marrakesh', 'Marrakesh')], string='Ville',
        default='agadir')
    project_units = fields.Text()
    units_lines = fields.One2many(comodel_name='project.units', inverse_name='project_id', string="Tools/Machines",
                                  copy=False)
    project_id = fields.Many2one(
        "project.units",
        string="Project")



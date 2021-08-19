
# -*- coding: utf-8 -*-
import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PayrollManagements(models.Model):
    _name = 'payrool.managements'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Payroll Managements'
    _rec_name = 'employee_id'

    @api.multi
    def name_get(self):
        # name get function for the model executes automatically
        res = []
        for rec in self:
            res.append((rec.id, '%s' % (rec.name_seq)))
        return res

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('payrool.managements.sequence') or _('New')
        result = super(PayrollManagements, self).create(vals)
        return result

    name_seq = fields.Char(string='ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))

    mois = fields.Date(string="Mois")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, track_visibility="always")
    project_id = fields.Many2one('project.costs', string='Projet', required=True, track_visibility="always")
    signed_contract = fields.Binary(
        string="Contrat", track_visibility="always")
    date_from = fields.Date(string='Date From', track_visibility="always", readonly=False, required=True,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)), )
    # states={'draft': [('readonly', False)]})

    date_to = fields.Date(string='Date To', track_visibility="always", readonly=False, required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), )
    # states={'draft': [('readonly', False)]})
    advance_payment = fields.Float(strins='Avances', readonly='True')

    notes = fields.Text(string="Registration Note")
    note = fields.Text()

    # cost_total_of_month = fields.Float(string="Salaire du mois", readonly=True)

    responsible = fields.Many2one("res.partner", string="Responsable")

    tooken_advanced = fields.Float(string="Total des avances", readonly=True)
    # remaining_salary = fields.Float(string="Salaire restant", readonly=True)

    line_salariee = fields.One2many("payroll.line", "salariee_mois", string='Salariee', track_visibility="always")
    line_advance_payment = fields.One2many("payroll.advance.line", "line_advance_payment", string='Salariee',
                                           track_visibility="always")

    cost_total_of_month = fields.Monetary(string='Salaire du mois', store=True, readonly=True,
                                          track_visibility='always')
    #tooken_advanced = fields.Monetary(string='Total des avances', store=True, readonly=True)
    remaining_salary = fields.Monetary(string='Salaire restant', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ouvert', 'Ouvert'),
        ('payé', 'Payé'),
    ], default='draft', track_visibility=True)




class PayrollLines(models.Model):
    _name = 'payroll.line'
    # pour les mois

    salariee_mois = fields.Many2one("payrool.managements", string="Situation D'Employée")

    reference = fields.Char(string='Référence')
    date = fields.Date(string='Mois', readonly=False, required=True,
                       default=lambda self: fields.Date.to_string(date.today()), )
    salaire_of_month = fields.Float(string="Salaire de Mois")
    tooken_advanced = fields.Float(string='Total des avances', store=True, readonly=True)
    remaining_salary = fields.Float(string='Salaire restant', store=True, readonly=True)

    line_salariee_jours = fields.Many2one("payroll.lines",string='Les jours', track_visibility="always")
    #line_salariee_jours = fields.One2many(comodel_name="payroll.lines",inverse_name="date", string='Les jours', track_visibility="always")

class PayrollLinesJours(models.Model):
    _name = 'payroll.lines'

    @api.multi
    def name_get(self):
        # name get function for the model executes automatically
        res = []
        for rec in self:
            res.append((rec.id, '%s' % (rec.date)))
        return res

    date = fields.Date(string='Jour', readonly=False, required=True,
                       default=lambda self: fields.Date.to_string(date.today()), )
    working_hour = fields.Float(string="Nombre D'Heure", default=8, required=True)
    price_per_hour = fields.Float(string='Prix Par Heure', default=10, required=True)
    # Total = fields.Float(string='Total de la journée')
    employee_total_amount = fields.Float(compute='_compute_day_total', string='Total de la journée')
    projects_id = fields.Many2one('project.costs', string='Projet', required=True, track_visibility="always")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, track_visibility="always")

    @api.depends('working_hour', 'price_per_hour', 'employee_total_amount')
    def _compute_day_total(self):
        for payroll in self:
            payroll.employee_total_amount = payroll.price_per_hour * payroll.working_hour

class PayrollAdvanceLines(models.Model):
    _name = 'payroll.advance.line'

    line_advance_payment = fields.Many2one("payrool.managements", string="Situation D'Employée")
    reference = fields.Char(string='Référence')
    date = fields.Date(string='Mois', readonly=False, required=True,
                       default=lambda self: fields.Date.to_string(date.today()), )
    description = fields.Char(string="Déscription")
    amount = fields.Float(string='Montant')
    motif = fields.Text(string='Motif')
    projects_id = fields.Many2one('project.costs', string='Projet', required=True, track_visibility="always")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, track_visibility="always")
    
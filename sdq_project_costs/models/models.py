# import dp as dp
from odoo import models, fields, api, _
from datetime import date, datetime, time


class Projectcosts(models.Model):
    _name = 'project.costs'
    _description = 'Project Costs'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'project_name'

    @api.multi
    def name_get(self):
        # name get function for the model executes automatically
        res = []
        for rec in self:
            res.append((rec.id, '%s - %s' % (rec.project_name, rec.name_seq)))
        return res

    # @api.model
    # def create(self, vals):
    #     if vals.get('name_seq', _('New')) == _('New'):
    #         vals['name_seq'] = self.env['ir.sequence'].next_by_code('project.costs.sequence') or _('New')
    #     result = super(projectinvoice, self).create(vals)
    #     return result

    name_seq = fields.Char(string='ID', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    photo = fields.Binary(string="Image", attachment=True)
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('invoiced', 'Invoiced'), ('done', 'Done'),
                              ('conceled', 'Conceled')], string='Status', readonly=True,
                             default='draft')
    product_id = fields.Many2one(
        "product.product",
        string="Description")
    project_name = fields.Char(string='Projet', required=True, track_visibility="always")
    project_description = fields.Text(string='Déscription', required=False, track_visibility="always")
    customer = fields.Many2one('res.partner', string='Client', track_visibility="always")
    project_responsable = fields.Many2one('res.partner', required=False, string='Chéf de projet',
                                          track_visibility="always")
    company_id = fields.Many2one(
        'res.company', readonly='True', string='Société',
        default=lambda self: self.env['res.company']._company_default_get())

    start_date = fields.Date('Date de début', track_visibility="always", required=True,
                             default=lambda self: fields.Date.to_string(date.today()), )
    end_date = fields.Date('Date de fin', track_visibility="always", required=True)
    adresse = fields.Char(string="Adresse", track_visibility="always", required=True)
    city = fields.Char(string="Ville", track_visibility="always", required=True, default='Agadir')
    notes = fields.Text(string="Registration Note")
    country_id = fields.Many2one('res.country', string="Country", required=True)
    total_costs = fields.Float(string='Coûts total réels ', store=True, readonly=True, compute='compute_total_total')
    # estimated_cost = fields.Float(string='Côut estimé ', store=True, readonly=True)
    tools_lines = fields.One2many(comodel_name='tools.costs', inverse_name='product_id', string="Tools/Machines",
                                  copy=False)
    service_lines = fields.One2many(comodel_name='service.costs', inverse_name='product_id', string="Service",
                                    copy=False)
    order_line = fields.One2many('renting.order.line', 'order_id', string='Renting details', copy=True)
    order_id = fields.Many2one('vehicle.renting.order', string='Order Reference', index=True, required=True,
                               ondelete='cascade')
    # units_lines = fields.One2many(comodel_name='project.units', inverse_name='project_id', string="Tools/Machines",
    #                               copy=False)
    overhead_lines = fields.One2many(comodel_name='overhead.costs', inverse_name='product_id', string="Overhead",
                                     copy=False)
    # total_tools_costs = fields.Float(string="Total d'outils", store=True, readonly=True)
    signed_contract = fields.Binary(
        string="Document signé", track_visibility="always")
    # project_id = fields.Many2one(
    #     "project.units",
    #     string="Project")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    # lines totals
    total_material_costs = fields.Float(string='Totale des Matériels', readonly=True, compute='compute_subtotal')
    total_service_costs = fields.Float(string='Totale des Services', readonly=True, compute='compute_service_subtotal')
    total_labour_costs = fields.Float(string="Totale  Main D'Oeuvre", readonly=True)
    total_overhead_costs = fields.Float(string="Totale D'Autre Charges", readonly=True,
                                        compute='compute_overhead_subtotal')
    total_renting_costs = fields.Float(string="Totale de location des véhicules", readonly=True,
                                       compute='compute_renting_subtotal')
    # total_tools_costs = fields.Float(string="Totale D'Autre Charges", readonly=True,
    #                                  compute='compute_tools_subtotal')
    total_contractor_costs = fields.Float(string="Totale D'Autre Charges", readonly=True)

    @api.depends('total_costs', 'total_material_costs', 'total_service_costs', 'total_overhead_costs')
    def compute_total_total(self):
        self.total_costs = self.total_material_costs + self.total_service_costs + self.total_overhead_costs

    @api.depends('tools_lines')
    def compute_subtotal(self):
        self.total_material_costs = 0
        if self.tools_lines:
            self.total_material_costs = sum(self.tools_lines.mapped('price_total'))

    @api.depends('service_lines')
    def compute_service_subtotal(self):
        self.total_renting_costs = 0
        if self.service_lines:
            self.total_service_costs = sum(self.service_lines.mapped('price_total'))

    @api.depends('overhead_lines')
    def compute_overhead_subtotal(self):
        self.total_overhead_costs = 0
        if self.overhead_lines:
            self.total_overhead_costs = sum(self.overhead_lines.mapped('price_total'))

    @api.depends('order_line')
    def compute_renting_subtotal(self):
        self.total_renting_costs = 0
        if self.order_line:
            self.total_renting_costs = sum(self.order_line.mapped('price_total'))

    @api.depends('tools_lines')
    def compute_tools_subtotal(self):
        self.total_tools_costs = 0
        if self.tools_lines:
            self.total_tools_costs = sum(self.tools_lines.mapped('price_total'))


class ProjectOutilcosts(models.Model):
    _name = 'tools.costs'
    _description = 'Tools Costs'

    product_id = fields.Many2one(
        "product.product",
        string="Description")
    # name = fields.Char(
    #     string="Description",
    #     required=True)
    qty = fields.Float(string="Quantity")
    uom_id = fields.Many2one(
        "uom.uom", string="Unit of Measure",
        required=True)
    price_unit = fields.Float('Unit Price', required=True, default=0.0)
    price_tax = fields.Float(string='Total Tax', store=True)
    tax_id = fields.Float(string='Taxes', store=True)
    price_total = fields.Float(string='Total TTC', readonly=True, store=True, compute='_compute_subtotal')
    price_subtotal = fields.Float(string='Total HT', readonly=True, store=True, compute='_compute_total')
    project_unit = fields.Char(string='Project Unit')
    project_unit_description = fields.Char(string='Déscription')
    project_unit_location = fields.Text(string='Adresse')

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id.id
        # self.name = self.product_id.name

    @api.depends('qty', 'price_unit', 'price_total', 'tax_id')
    def _compute_subtotal(self):
        for each in self:
            each.price_total = 0
            tax_id = 0
            if each.tax_id:
                tax_id = (each.price_unit * each.qty) * each.tax_id / 100
            each.price_total = tax_id + (each.qty * each.price_unit)

    @api.depends('qty', 'price_unit', 'price_total')
    def _compute_total(self):
        for each in self:
            each.price_total = 0
            tax_id = 0
            each.price_total = each.qty * each.price_unit


class ProjectServicecosts(models.Model):
    _name = 'service.costs'
    _description = 'Service Costs'

    product_id = fields.Many2one(
        "product.product",
        string="Description")
    name = fields.Char(
        string="Description")
    # service_costs = fields.Char(string='Service Lié du Projet')
    qty = fields.Float(string="Quantity")
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        required=True, default='day')
    price_unit = fields.Float('Unit Price', required=True, default=0.0)
    price_tax = fields.Float(string='Total Tax', store=True)
    tax_id = fields.Float(string='Taxes', store=True)
    price_total = fields.Float(string='Total TTC', readonly=True, store=True, compute='_compute_subtotal')

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id.id

    @api.depends('qty', 'price_unit', 'price_total', 'tax_id')
    def _compute_subtotal(self):
        for each in self:
            each.price_total = 0
            tax_id = 0
            if each.tax_id:
                tax_id = (each.price_unit * each.qty) * each.tax_id / 100
            each.price_total = tax_id + (each.qty * each.price_unit)


class ProjectOverheadcosts(models.Model):
    _name = 'overhead.costs'
    _description = 'Overhead Costs'

    product_id = fields.Many2one(
        "product.product",
        string="Product")
    name = fields.Char(
        string="Description",
        compute='_onchange_product_id')
    qty = fields.Float(string="Quantity")
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        required=True, default='day')
    price_unit = fields.Float('Unit Price', required=True, default=0.0)
    price_tax = fields.Float(string='Total Tax', store=True)
    tax_id = fields.Float(string='Taxes', store=True)
    price_total = fields.Float(string='Total TTC', readonly=True, store=True, compute='_compute_subtotal')

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id.id

    @api.depends('qty', 'price_unit', 'price_total', 'tax_id')
    def _compute_subtotal(self):
        for each in self:
            each.price_total = 0
            tax_id = 0
            if each.tax_id:
                tax_id = (each.price_unit * each.qty) * each.tax_id / 100
            each.price_total = tax_id + (each.qty * each.price_unit)

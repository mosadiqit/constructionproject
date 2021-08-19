# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError


class VehicleRentingOrder(models.Model):
    _name = 'vehicle.renting.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'description'
    _order = 'date desc, id desc'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' or rec.is_canceled is True:
                raise UserError('You can not delete this order')
            super(VehicleRentingOrder, rec).unlink()

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('rent')
        vals.update({
            'name': name
        })
        return super(VehicleRentingOrder, self).create(vals)

    name = fields.Char(string='Order Sequence', readonly=True, required=True, default=" ")
    order_for_renting_number = fields.Char(string='Renting Order N°:', required=True)
    order_sequence = fields.Char(string='Sequence:', required=True)

    partner_id = fields.Many2one('res.partner', domain="[('supplier', '=', True)]", string='Supplier')
    vehicle_id = fields.Many2one(comodel_name='fleet', string='Vehicle')
    vehicle_type = fields.Many2one(string='Vehicle Type')

    date = fields.Date('Date', default=datetime.now().strftime('%Y-%m-%d'))
    project_id = fields.Many2one('project.costs', string='Project')
    driver = fields.Char(string='Driver')
    responsible_id = fields.Many2one('hr.employee', string='Responsible')

    order_line = fields.One2many('renting.order.line', 'order_id', string='Renting details', copy=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)

    @api.depends('order_line.price_total', 'order_line.price_subtotal', 'order_line.price_tax')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    amount_untaxed = fields.Float(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                  track_visibility='always')
    amount_tax = fields.Float(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To approve'),
        ('approved', 'Approved'),
        ('invoiced', 'Invoiced'),
        ('canceled', 'Canceled'),
    ], default='draft', track_visibility=True)

    notes = fields.Text()
    is_canceled = fields.Boolean(default=False)
    is_invoiced = fields.Boolean(default=False)
    inv_ref_id = fields.Many2one('account.invoice', string='reference invoice')

    @api.multi
    def confirm_order(self):
        if not self.order_line:
            raise UserError('You did not add details of renting')
        if self.state == 'draft':
            self.write({'state': 'to_approve'})

    @api.multi
    def cancel_order(self):
        for rec in self:
            if rec.state == 'to_approve':
                rec.write({'state': 'canceled'})

    @api.multi
    def return_to_draft(self):
        for rec in self:
            if rec.state == 'canceled':
                rec.write({'state': 'draft', 'is_canceled': True})

    @api.multi
    def validate_order(self):
        if self.state == 'to_approve':
            self.write({'state': 'approved'})

    def cancel_invoiced_state(self):
        for rec in self:
            if rec.state == 'invoiced':
                for line in rec.inv_ref_id.invoice_line_ids:
                    print(line.renting_id)
                    print(rec)
                    if line.renting_id == rec:
                        raise UserError('You should Concel the invoice before Modify it ')
                    else:
                        rec.write({
                            'state': 'approved',
                            'inv_ref_id': False
                        })


class RentingOrderLine(models.Model):
    _name = 'renting.order.line'
    _description = 'renting order line'

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Renting Type', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)
    product_qty = fields.Float(string='Quantity', default=1.0, required=True)
    product_uom = fields.Many2one('uom.uom', string='UoM', required=True, related='product_id.uom_po_id')
    price_unit = fields.Float(string='Unit Price', required=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    order_id = fields.Many2one('vehicle.renting.order', string='Order Reference', index=True, required=True,
                               ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    vehicle_id = fields.Many2one(comodel_name='fleet', string='Vehicle')

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.name = self.product_id.name
        self.price_unit = self.product_id.standard_price
        return result

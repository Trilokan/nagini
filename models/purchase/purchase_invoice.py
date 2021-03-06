# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime
from .. import calculation


PROGRESS_INFO = [('draft', 'Draft'), ('approved', 'approved'), ('cancel', 'Cancel')]
INVOICE_TYPE = [("dpo", "Direct Purchase Bill"), ("po", "Purchase Bill")]
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
CURRENT_INDIA = datetime.now().strftime("%d-%m-%Y %H:%M:%S")


# Bills
class PurchaseInvoice(models.Model):
    _name = "purchase.invoice"
    _inherit = "mail.thread"

    date = fields.Date(srring="Date", required=True, default=CURRENT_DATE)
    name = fields.Char(string="Name", readonly=True)
    person_id = fields.Many2one(comodel_name="lam.person", string="Partner", required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", readdonly=True)
    indent_id = fields.Many2one(comodel_name="purchase.indent", string="Purchase Indent")
    quote_id = fields.Many2one(comodel_name="purchase.quote", string="Quotation")
    po_id = fields.Many2one(comodel_name="purchase.order", string="Purchase Order")
    receipt_id = fields.Many2one(comodel_name="material.receipt", string="Material Receipt")
    direct_receipt_id = fields.Many2one(comodel_name="direct.material.receipt", string="Material Receipt")
    reference = fields.Char(string="Reference")
    invoice_detail = fields.One2many(comodel_name="purchase.invoice.detail", inverse_name="invoice_id")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    invoice_type = fields.Selection(selection=INVOICE_TYPE, string="Invoice Type", required=True)
    discounted_amount = fields.Float(string="Discounted Amount", readonly=True)
    untaxed_amount = fields.Float(string="Untaxed Amount", readonly=True)
    taxed_amount = fields.Float(string="Taxed Amount", readonly=True)
    cgst = fields.Float(string="CGST", readonly=True)
    sgst = fields.Float(string="SGST", readonly=True)
    igst = fields.Float(string="IGST", readonly=True)
    gross_amount = fields.Float(stringt="Gross Amount", readonly=True)

    sub_total_amount = fields.Float(string='Sub Total', readonly=True)
    discount_amount = fields.Float(string='Discount Amount', readonly=True, help='Discount value')
    total_amount = fields.Float(string='Total', readonly=True)
    tax_amount = fields.Float(string='Tax Amount', readonly=True, help='Tax value')
    round_off_amount = fields.Float(string='Round-Off', readonly=True)
    grand_total_amount = fields.Float(string='Grand Total', readonly=True)

    expected_delivery = fields.Char(string='Expected Delivery')
    freight = fields.Char(string='Freight')
    payment = fields.Char(string='Payment')
    insurance = fields.Char(string='Insurance')
    certificate = fields.Char(string='Certificate')
    warranty = fields.Char(string='Warranty')

    writter = fields.Text(string="Writter", track_visibility='always')

    # payment_detail = fields.One2many(comodel_name="invoice.detail",
    #                                  inverse_name="invoice_id",
    #                                  string="Invoice detail")
    # Account_detail

    def generate_journal_entries(self, recs):
        item_ids = []
        for rec in recs:
            item_ids.append((0, 0, {"description": 0,
                                    "person_id": self.person_id.id,
                                    "account_id": 0,
                                    "credit": 0,
                                    "debit": 0}))

        if item_ids:
            entry = {"journal_id": 0,
                     "period_id": 0,
                     "reference": self.name,
                     "item_ids": item_ids}

            self.env["journal.entries"].create(entry)

    @api.multi
    def trigger_approve(self):
        self.total_calculation()
        self.generate_journal_entries()

        writter = "Invoice approved by {0}".format(self.env.user.name)
        self.write({"progress": "approved", "writter": writter})

    @api.multi
    def trigger_cancel(self):
        self.total_calculation()

        writter = "Invoice cancel by {0}".format(self.env.user.name)
        self.write({"progress": "cancel", "writter": writter})

    @api.multi
    def total_calculation(self):
        recs = self.invoice_detail

        if not recs:
            raise exceptions.ValidationError("Error! Bill details not found")

        for rec in recs:
            rec.detail_calculation()

        discount_amount = discounted_amount = tax_amount = untaxed_amount = taxed_amount \
            = cgst = sgst = igst = sub_total_amount = 0

        for rec in recs:
            discount_amount = discount_amount + rec.discount_amount
            discounted_amount = discounted_amount + rec.discounted_amount
            tax_amount = tax_amount + rec.tax_amount
            untaxed_amount = untaxed_amount + rec.untaxed_amount
            taxed_amount = taxed_amount + rec.taxed_amount
            cgst = cgst + rec.cgst
            sgst = sgst + rec.sgst
            igst = igst + rec.igst
            sub_total_amount = sub_total_amount + rec.total_amount

        total_amount = sub_total_amount - discount_amount
        grand_total_amount = round(total_amount + tax_amount)
        round_off_amount = round(total_amount + tax_amount) - (total_amount + tax_amount)

        self.write({"discount_amount": discount_amount,
                    "discounted_amount": discounted_amount,
                    "tax_amount": tax_amount,
                    "untaxed_amount": untaxed_amount,
                    "taxed_amount": taxed_amount,
                    "cgst": cgst,
                    "sgst": sgst,
                    "igst": igst,
                    "sub_total_amount": sub_total_amount,
                    "total_amount": total_amount,
                    "grand_total_amount": grand_total_amount,
                    "round_off_amount": round_off_amount})

    @api.model
    def create(self, vals):
        code = "{0}.{1}".format("purchase.invoice", vals["invoice_type"])
        vals['name'] = self.env['ir.sequence'].next_by_code(code)
        return super(PurchaseInvoice, self).create(vals)


class InvoiceDetail(models.Model):
    _name = "purchase.invoice.detail"

    person_id = fields.Many2one(comodel_name="lam.person", string="Vendor", readonly=True)
    product_id = fields.Many2one(comodel_name="hos.product", string="Description", required=True)
    description = fields.Text(string="Item Description", readonly=True)
    uom_id = fields.Many2one(comodel_name="product.uom", string="UOM", related="product_id.uom_id")
    unit_price = fields.Float(string="Unit Price")
    quantity = fields.Float(string="Quantity", required=True)
    discount = fields.Float(string="Discount")
    tax_id = fields.Many2one(comodel_name="product.tax", string="Tax")
    total_amount = fields.Float(string="Total Amount", readonly=True)
    cgst = fields.Float(string="CGST", readonly=True)
    sgst = fields.Float(string="SGST", readonly=True)
    igst = fields.Float(string="IGST", readonly=True)
    tax_amount = fields.Float(string="Tax Amount", readonly=True)
    discount_amount = fields.Float(string="Discount Amount", readonly=True)
    discounted_amount = fields.Float(string="Discounted Amount", readonly=True)
    untaxed_amount = fields.Float(string="Untaxed Value", readonly=True)
    taxed_amount = fields.Float(string="Taxed value", readonly=True)
    invoice_id = fields.Many2one(comodel_name="purchase.invoice", string="Hospital Invoice")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", related="invoice_id.progress")

    @api.multi
    def detail_calculation(self):
        state = "outer_state"
        if self.person_id.state_id.id == self.env.user.company_id.state_id.id:
            state = "inter_state"

        data = calculation.purchase_calculation(self.unit_price,
                                                self.quantity,
                                                self.discount,
                                                self.tax_id.rate,
                                                state)
        self.write(data)

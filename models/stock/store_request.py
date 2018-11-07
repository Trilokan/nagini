# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime

PROGRESS_INFO = [("draft", "Draft"), ("confirmed", "Confirmed"), ("approved", "Approved"), ("cancel", "Cancel")]
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
CURRENT_INDIA = datetime.now().strftime("%d-%m-%Y %H:%M:%S")


class StoreRequest(models.Model):
    _name = "store.request"
    _inherit = "mail.thread"

    date = fields.Date(string="Date", required=True, default=CURRENT_DATE)
    name = fields.Char(string="Name", readonly=True)
    department_id = fields.Many2one(comodel_name="hos.department", string="Department", required=True)
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress")
    request_detail = fields.One2many(comodel_name="store.request.detail", inverse_name="request_id", string="Request Detail")
    writter = fields.Char(string="Writter", track_visibility="always")

    @api.multi
    def trigger_confirm(self):
        writter = "Store Request Confirmed by {0} on {1}".format(self.env.user.name, CURRENT_INDIA)
        self.write({"progress": "confirmed", "writter": writter})

    @api.multi
    def trigger_cancel(self):
        writter = "Store Request cancel by {0} on {1}".format(self.env.user.name, CURRENT_INDIA)
        self.write({"progress": "cancel", "writter": writter})

    def generate_issue(self, recs):
        issue_detail = []
        for rec in recs:
            issue_detail.append((0, 0, {"product_id": rec.product_id.id,
                                        "description": rec.description,
                                        "requested_quantity": rec.quantity,
                                        "issued_quantity": 0}))

        if issue_detail:
            issue = {"request_id": self.id,
                     "issue_detail": issue_detail}

            self.env["store.issue"].create(issue)

    @api.multi
    def trigger_approved(self):
        recs = self.env["store.request.detail"].search([("request_id", "=", self.id), ("quantity", ">", 0)])

        if not recs:
            raise exceptions.ValidationError("Error! No Products found")

        self.generate_issue(recs)

        writter = "Store Request Approved by {0} on {1}".format(self.env.user.name, CURRENT_INDIA)
        self.write({"progress": "approved", "writter": writter})

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code(self._name)
        return super(StoreRequest, self).create(vals)


class StoreRequestDetail(models.Model):
    _name = "store.request.detail"

    name = fields.Char(string="Name", readonly=True)
    product_id = fields.Many2one(comodel_name="hos.product", string="Item", required=True)
    description = fields.Text(string="Item Description")
    uom_id = fields.Many2one(comodel_name="product.uom", string="UOM", related="product_id.uom_id")
    requested_quantity = fields.Float(string="Request Quantity")
    quantity = fields.Float(string="Quantity")
    request_id = fields.Many2one(comodel_name="store.request", string="Store Request")

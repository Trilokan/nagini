# -*- coding: utf-8 -GPK*-

from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta
from calendar import monthrange

PROGRESS_INFO = [("draft", "Draft"), ("open", "Open"), ("closed", "Closed")]


class Period(models.Model):
    _name = "period.period"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)
    year_id = fields.Many2one(comodel_name="year.year", string="Year", readonly=True)
    from_date = fields.Date(string="From Date", readonly=True)
    till_date = fields.Date(string="Till Date", readonly=True)
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft", track_visibility="always")
    writter = fields.Text(string="Writter", track_visibility="always")

    _sql_constraints = [('unique_period', 'unique (name)', 'Error! Monthly period must be unique')]

    @api.multi
    def trigger_period_open(self):
        self.check_progress([("progress", "=", "open")])
        writter = "Period opened by {0}".format(self.env.user.name)
        self.write({"progress": "open", "writter": writter})

    @api.multi
    def trigger_period_closed(self):
        self.check_progress([("progress", "=", "open"), ("id", "!=", self.id)])
        writter = "Period closed by {0}".format(self.env.user.name)
        self.write({"progress": "closed", "writter": writter})

    def check_progress(self, data):
        if self.env["period.period"].search(data):
            raise exceptions.ValidationError("Error! Please close the existing period before open new period")

    @api.model
    def create(self, vals):
        from_date = datetime.strptime(vals["from_date"], "%Y-%m-%d")
        vals["name"] = "{0} {1}".format(from_date.strftime("%B"), from_date.strftime("%Y"))

        return super(Period, self).create(vals)

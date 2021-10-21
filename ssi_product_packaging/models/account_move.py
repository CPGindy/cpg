from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sku_lookup = fields.Char(compute="_compute_customer_sku", string="SKU Lookup")

    @api.depends('product_id')
    def _compute_customer_sku(self):
        for rec in self:
            if rec.product_id and rec.product_id.sku_lookup_line:
                sku = rec.product_id.sku_lookup_line.filtered(lambda line: line.partner_id.id == rec.partner_id.id)
                if sku:
                    rec.sku_lookup = sku[0].customer_sku
                else:
                    rec.sku_lookup = ''
            else:
                rec.sku_lookup = ''


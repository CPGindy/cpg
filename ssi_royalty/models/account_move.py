# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from itertools import groupby, combinations
from datetime import date


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    def _post(self, soft=True):
        posted = super()._post(soft=soft)
#         search_royalty = self.env['ssi_royalty.ssi_royalty'].search([('invoice_id', '=', posted.id)])
#         if search_royalty:
#             for royalty in search_royalty:
#                 royalty.unlink()
        for royalty in self.env['ssi_royalty.ssi_royalty'].search([('invoice_id', '=', posted.id)]):
            royalty.unlink()
        for rec in self:
            if rec.invoice_line_ids:
                # Non kit products
                for invoice_line in rec.invoice_line_ids.filtered(
                    lambda pro: pro.product_id.license_product and not (
                        pro.product_id.bom_ids and pro.product_id.bom_ids[0].type == "phantom"
                    ) and pro.move_id.move_type != 'in_invoice'
                ):
                    royaltable_amount = float(invoice_line.price_subtotal) / len(invoice_line.product_id.license_product.filtered(
                        lambda license: license.license_item_id.end_date >= date.today()
                    ))
                    for lic_prod in invoice_line.product_id.license_product.filtered(
                        lambda license: license.license_item_id.end_date >= date.today()
                    ):
                        data = {
                            'licensed_item' : lic_prod.license_item_id.id,
                            'license_product_id': lic_prod.id,
                            'license_id' : lic_prod.license_item_id.license_id.id,
                            'artist_id': lic_prod.license_item_id.license_id.artist_id.id,
                            'type': 'sale_on_item',
                            'item_value': royaltable_amount,
                            'licensor_id': lic_prod.license_item_id.license_id.licensor_id.id,
                            'date': date.today(),
                            'source_document': posted['name'],
                            'payment_status': 'draft',
                            'royalty_rate': lic_prod.royalty_rate,
                            'royalty_value': royaltable_amount * lic_prod.royalty_rate,
                            'invoice_id': posted.id,
                        }
                        royalty = self.env['ssi_royalty.ssi_royalty'].create(data)
                        for pool in lic_prod.license_item_id.item_pool_id.filtered(lambda p: not p.first_sale_date and p.status == 'paid'):
                            pool.update({'first_sale_date': date.today()})
                            
                            search_pool_rec = self.env['ssi_royalty.pool'].search([('artist_id', '=', royalty.artist_id.id)])
                            if search_pool_rec:
                                line_vals = {
                                    'date': date.today(),
                                    'memo': pool.license_item_id.art_license_number,
                                    'value_type': 'in',
                                    'pool_value': pool.value,
                                    'value': pool.value + search_pool_rec.balance,
                                    'pool_id': search_pool_rec.id
                                }
                                self.env['ssi_royalty.pool.line'].create(line_vals)
                                search_pool_rec.update({'balance': line_vals['value']})
                            elif royalty.artist_id:
                               pool_val = {
                                   'artist_id': royalty.artist_id.id,
                                   'licensor_id': royalty.licensor_id.id or False,
                                   'balance': 0.0
                               } 
                               pool_id = self.env['ssi_royalty.pool'].create(pool_val)
                               line_vals = {
                                    'pool_id': pool_id.id,
                                    'date': date.today(),
                                    'memo': pool.license_item_id.art_license_number,
                                    'value_type': 'in',
                                    'pool_value': pool.value,
                                    'value': pool.value + pool_id.balance

                                }
                               self.env['ssi_royalty.pool.line'].create(line_vals)
                               pool_id.update({'balance': line_vals['value']})
                # Kit products
                for invoice_line in rec.invoice_line_ids.filtered(
                    lambda pro: pro.product_id.bom_ids and pro.product_id.bom_ids[0].type == "phantom" and pro.move_id.move_type != 'in_invoice'
                ):
                    components = invoice_line.product_id.bom_ids[0].bom_line_ids
                    
                    # calculate amount of components on which a royalty applies
                    royaltable_components = []
                    for component in components:
                        product = component.product_id
                        if any([license.license_item_id.end_date >= date.today() for license in product.license_product]):
                            royaltable_components.append(component)
                    
                    royaltable_amount = float(invoice_line.price_subtotal) / len(royaltable_components)
                    for r_component in royaltable_components:
                        artwork_count = len(r_component.product_id.license_product.filtered(
                            lambda license: license.license_item_id.end_date >= date.today()))
                        
                        for lic_prod in r_component.product_id.license_product.filtered(
                            lambda license: license.license_item_id.end_date >= date.today()
                        ):
                            data = {
                                'licensed_item' : lic_prod.license_item_id.id,
                                'license_product_id': lic_prod.id,
                                'license_id' : lic_prod.license_item_id.license_id.id,
                                'artist_id': lic_prod.license_item_id.license_id.artist_id.id,
                                'type': 'sale_on_item',
                                'item_value': royaltable_amount / artwork_count,
                                'licensor_id': lic_prod.license_item_id.license_id.licensor_id.id,
                                'date': date.today(),
                                'source_document': posted['name'],
                                'payment_status': 'draft',
                                'royalty_rate': lic_prod.royalty_rate,
                                'royalty_value': (royaltable_amount/artwork_count) * lic_prod.royalty_rate,
                                'invoice_id': posted.id,
                            }
                            royalty = self.env['ssi_royalty.ssi_royalty'].create(data)
                            for pool in lic_prod.license_item_id.item_pool_id.filtered(lambda p: not p.first_sale_date and p.status == 'paid'):
                                pool.update({'first_sale_date': date.today()})

                                search_pool_rec = self.env['ssi_royalty.pool'].search([('artist_id', '=', royalty.artist_id.id)])
                                if search_pool_rec:
                                    line_vals = {
                                        'date': date.today(),
                                        'memo': pool.license_item_id.art_license_number,
                                        'value_type': 'in',
                                        'pool_value': pool.value,
                                        'value': pool.value + search_pool_rec.balance,
                                        'pool_id': search_pool_rec.id
                                    }
                                    self.env['ssi_royalty.pool.line'].create(line_vals)
                                    search_pool_rec.update({'balance': line_vals['value']})
                                elif royalty.artist_id:
                                   pool_val = {
                                       'artist_id': royalty.artist_id.id,
                                       'licensor_id': royalty.licensor_id.id or False,
                                       'balance': 0.0
                                   } 
                                   pool_id = self.env['ssi_royalty.pool'].create(pool_val)
                                   line_vals = {
                                        'pool_id': pool_id.id,
                                        'date': date.today(),
                                        'memo': pool.license_item_id.art_license_number,
                                        'value_type': 'in',
                                        'pool_value': pool.value,
                                        'value': pool.value + pool_id.balance

                                    }
                                   self.env['ssi_royalty.pool.line'].create(line_vals)
                                   pool_id.update({'balance': line_vals['value']})
        return posted
    
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    royalty_id = fields.Many2one('ssi_royalty.ssi_royalty', string='Royalty')
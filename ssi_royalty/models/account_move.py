# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from itertools import groupby, combinations
from datetime import date


class AccountMove(models.Model):
    _inherit = 'account.move'

    royalty_count = fields.Integer(string="Royalty Count", compute='_get_royalty_count')


    def _get_royalty_count(self):
        for record in self:
            royalty_count = self.env['ssi_royalty.ssi_royalty'].sudo().search_count([('invoice_id', '=', record.id)])
            record.royalty_count = royalty_count


    def action_view_royalty(self):
        royalty_lines = self.env['ssi_royalty.ssi_royalty'].search([('invoice_id', '=', self.id)])
        royalty_ids = []
        for line in royalty_lines:
            royalty_ids.append(line.id)
        if len(royalty_ids) == 1:
            return {
                'name': _('Royalty'),
                'view_mode': 'form',
                'view_id': self.env.ref('ssi_royalty.ssi_royalty_view_form').id,
                'view_type': 'form',
                'res_model': 'ssi_royalty.ssi_royalty',
                'type': 'ir.actions.act_window',
                'res_id': royalty_lines.id,
                'target': 'current',
            }
        else:
            return {
                'name': _('Royalties'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'ssi_royalty.ssi_royalty',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', royalty_ids)],
                'target': 'current',
            }        


    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        # search_royalty = self.env['ssi_royalty.ssi_royalty'].search([('invoice_id', '=', posted.id)])
        # if search_royalty:
        #     for royalty in search_royalty:
        #         royalty.unlink()
        # if self.move_type == 'out_invoice':
        for royalty in self.env['ssi_royalty.ssi_royalty'].search([('invoice_id', 'in', posted.filtered(lambda r: r.move_type == 'out_invoice').ids)]):
            royalty.unlink()
        for rec in posted:
            if rec.move_type == 'out_invoice':
                if rec.invoice_line_ids:
#                     for invoice_line in rec.invoice_line_ids.filtered(
#                         lambda pro: not pro.product_id.license_product and not (
#                             pro.product_id.bom_ids and pro.product_id.bom_ids[0].type == "phantom"
#                         ) and pro.move_id.move_type != 'in_invoice'
#                     ):
#                         data = {
#                             'invoice_product_id': invoice_line.product_id.id,
#                             'licensed_item': False,
#                             'license_product_id': False,
#                             'license_id': False,
#                             'artist_id': False,
#                             'type': 'not_licensed',
#                             'item_value': float(invoice_line.price_subtotal),
#                             'licensor_id': False,
#                             'date': date.today(),
#                             'source_document': rec['name'],
#                             'payment_status': 'draft',
#                             'royalty_rate': 0,
#                             'royalty_value': 0,
#                             'invoice_id': rec.id,
#                         }
                    
                    #Create Zero royalties for the products whose license item doesnot exist
                    for invoice_line in rec.invoice_line_ids.filtered(
                        lambda pro: not pro.product_id.license_product and not (
                            pro.product_id.bom_ids and pro.product_id.bom_ids[0].type == "phantom"
                        ) and pro.move_id.move_type != 'in_invoice'
                    ):
                        data = {
                            'invoice_product_id': invoice_line.product_id.id,
                            'type': 'not_licensed',
                            'item_value': float(invoice_line.price_subtotal),
                            'date': date.today(),
                            'source_document': rec['name'],
                            'payment_status': 'draft',
                            'royalty_rate': 0.0,
                            'royalty_value': 0.0,
                            'invoice_id': rec.id,
                        }
                        self.env['ssi_royalty.ssi_royalty'].create(data)

                    # Non kit products
                    for invoice_line in rec.invoice_line_ids.filtered(
                        lambda pro: pro.product_id.license_product and not (
                            pro.product_id.bom_ids and pro.product_id.bom_ids[0].type == "phantom"
                        ) and pro.move_id.move_type != 'in_invoice'
                    ):
                        # royaltable_amount = float(invoice_line.price_subtotal) / len(invoice_line.product_id.license_product.filtered(
                        #     lambda license: license.license_item_id.end_date and license.license_item_id.end_date >= date.today()
                        # ))
                        if len(invoice_line.product_id.license_product.filtered(lambda license: license.license_item_id.license_status in ['active', 'revise', 'pending'])) > 0:
                            royaltable_amount = float(invoice_line.price_subtotal) / len(invoice_line.product_id.license_product.filtered(
                                lambda license: license.license_item_id.license_status in ['active', 'revise', 'pending']
                            ))

                            # for lic_prod in invoice_line.product_id.license_product.filtered(
                            #     lambda license: license.license_item_id.end_date and license.license_item_id.end_date >= date.today()
                            # ):
                            for lic_prod in invoice_line.product_id.license_product.filtered(
                                lambda license: license.license_item_id.license_status in ['active', 'revise', 'pending']
                            ):
                                if lic_prod.license_item_id.license_type != 'flat':
                                    type = 'sale_on_item'
                                    royalty_rate = lic_prod.royalty_rate
                                    royalty_value = royaltable_amount * lic_prod.royalty_rate
                                elif lic_prod.license_item_id.license_type == 'flat':
                                    type = 'flat_fee'
                                    royalty_rate = 0.0
                                    royalty_value = 0.0
                                data = {
                                    'licensed_item' : lic_prod.license_item_id.id,
                                    'license_product_id': lic_prod.id,
                                    'invoice_product_id': invoice_line.product_id.id,
                                    'license_id' : lic_prod.license_item_id.license_id.id,
                                    'artist_id': lic_prod.license_item_id.license_id.artist_id.id,
                                    'type': type,
                                    'item_value': royaltable_amount,
                                    'licensor_id': lic_prod.license_item_id.license_id.licensor_id.id,
                                    'date': date.today(),
                                    'source_document': rec['name'],
                                    'payment_status': 'draft',
                                    'royalty_rate': royalty_rate,
                                    'royalty_value': royalty_value,
                                    'invoice_id': rec.id,
                                }
                                royalty = self.env['ssi_royalty.ssi_royalty'].create(data)
                                for pool in lic_prod.license_item_id.item_pool_id.filtered(lambda p: not p.first_sale_date):
                                    pool.update({'first_sale_date': date.today()})

                                    search_pool_rec = self.env['ssi_royalty.pool'].search([('artist_id', '=', royalty.artist_id.id)])
                                    if search_pool_rec:
                                        line_vals = {
                                            'date': date.today(),
                                            'memo': pool.art_id.art_license_number,
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
                                            'memo': pool.art_id.art_license_number,
                                            'value_type': 'in',
                                            'pool_value': pool.value,
                                            'value': pool.value + pool_id.balance
                                        }
                                        self.env['ssi_royalty.pool.line'].create(line_vals)
                                        pool_id.update({'balance': line_vals['value']})
                                        
                        #Create Zero royalties for the products whose license item are in inactive stages, updated from decision tree on 12/16/2021
                        if len(invoice_line.product_id.license_product.filtered(lambda license: license.license_item_id.license_status == 'inactive')) > 0:
                            royaltable_amount = float(invoice_line.price_subtotal) / len(invoice_line.product_id.license_product.filtered(
                                lambda license: license.license_item_id.license_status == 'inactive'
                            ))
                            for lic_prod in invoice_line.product_id.license_product.filtered(lambda license: license.license_item_id.license_status == 'inactive'):
                                data = {
                                        'licensed_item' : lic_prod.license_item_id.id,
                                        'license_product_id': lic_prod.id,
                                        'invoice_product_id': invoice_line.product_id.id,
                                        'license_id' : lic_prod.license_item_id.license_id.id,
                                        'artist_id': lic_prod.license_item_id.license_id.artist_id.id,
                                        'type': 'not_licensed',
                                        'item_value': royaltable_amount,
                                        'licensor_id': lic_prod.license_item_id.license_id.licensor_id.id,
                                        'date': date.today(),
                                        'source_document': rec['name'],
                                        'payment_status': 'draft',
                                        'royalty_rate': royalty_rate,
                                        'royalty_value': 0.0,
                                        'invoice_id': rec.id,
                                    }
                                self.env['ssi_royalty.ssi_royalty'].create(data)

                    # Kit products
                    for invoice_line in rec.invoice_line_ids.filtered(
                        lambda pro: pro.product_id.bom_ids and pro.product_id.bom_ids[0].type == "phantom" and pro.move_id.move_type != 'in_invoice'
                    ):
                        components = invoice_line.product_id.bom_ids[0].bom_line_ids

                        # calculate amount of components on which a royalty applies
                        royaltable_components = []
                        inactive_components = []
                        non_licensed_components = []
                        
                        for component in components:
                            product = component.product_id
                            if any([license.license_item_id.license_status in ['active', 'revise', 'pending'] for license in product.license_product]):
                                royaltable_components.append(component)
                            if any([license.license_item_id.license_status == 'inactive' for license in product.license_product]):
                                inactive_components.append(component)
                            if not product.license_product:
                                non_licensed_components.append(component)

                        component_count = len(royaltable_components) + len(inactive_components) + len(non_licensed_components)

                        #Create Zero royalties for the kit products who dont have license or whose license item are in inactive stages, updated from decision tree on 12/16/2021
                        if non_licensed_components:
                            royaltable_amount = float(invoice_line.price_subtotal) / test
                            for n_component in non_licensed_components:
                                data = {
                                    'invoice_product_id': n_component.product_id.id,
                                    'type': 'not_licensed',
                                    'item_value': royaltable_amount,
                                    'date': date.today(),
                                    'source_document': rec['name'],
                                    'payment_status': 'draft',
                                    'royalty_rate': 0.0,
                                    'royalty_value': 0.0,
                                    'invoice_id': rec.id,
                                }
                                self.env['ssi_royalty.ssi_royalty'].create(data)

                        if inactive_components:
                            inactive_royaltable_amount = float(invoice_line.price_subtotal) / test
                            for i_component in inactive_components:
                                artwork_count = len(i_component)
                                for lic_prod in i_component.product_id.license_product.filtered(
                                    lambda license: license.license_item_id.license_status in ['inactive']
                                ):
                                    data = {
                                        'licensed_item' : lic_prod.license_item_id.id,
                                        'license_product_id': lic_prod.id,
                                        'invoice_product_id': invoice_line.product_id.id,
                                        'license_id' : lic_prod.license_item_id.license_id.id,
                                        'artist_id': lic_prod.license_item_id.license_id.artist_id.id,
                                        'type': 'not_licensed',
                                        'item_value': inactive_royaltable_amount / artwork_count,
                                        'licensor_id': lic_prod.license_item_id.license_id.licensor_id.id,
                                        'date': date.today(),
                                        'source_document': rec['name'],
                                        'payment_status': 'draft',
                                        'royalty_rate': 0.0,
                                        'royalty_value': 0.0,
                                        'invoice_id': rec.id,
                                    }
                                    self.env['ssi_royalty.ssi_royalty'].create(data)


                        if royaltable_components:
                            royaltable_amount = float(invoice_line.price_subtotal) / test
                            for r_component in royaltable_components:
                                artwork_count = len(r_component.product_id.license_product.filtered(
                                    lambda license: license.license_item_id.license_status in ['active', 'revise', 'pending']))

                                for lic_prod in r_component.product_id.license_product.filtered(
                                    lambda license: license.license_item_id.license_status in ['active', 'revise', 'pending']
                                ):
                                    if lic_prod.license_item_id.license_type != 'flat':
                                        type = 'sale_on_item'
                                        royalty_rate = lic_prod.royalty_rate
                                        royalty_value = (royaltable_amount/artwork_count) * lic_prod.royalty_rate

                                    elif lic_prod.license_item_id.license_type == 'flat':
                                        type = 'flat_fee'
                                        royalty_rate = 0.0
                                        royalty_value = 0.0

                                    data = {
                                        'licensed_item' : lic_prod.license_item_id.id,
                                        'license_product_id': lic_prod.id,
                                        'invoice_product_id': invoice_line.product_id.id,
                                        'license_id' : lic_prod.license_item_id.license_id.id,
                                        'artist_id': lic_prod.license_item_id.license_id.artist_id.id,
                                        'type': type,
                                        'item_value': royaltable_amount / artwork_count,
                                        'licensor_id': lic_prod.license_item_id.license_id.licensor_id.id,
                                        'date': date.today(),
                                        'source_document': rec['name'],
                                        'payment_status': 'draft',
                                        'royalty_rate': royalty_rate,
                                        'royalty_value': royalty_value,
                                        'invoice_id': rec.id,
                                    }
                                    royalty = self.env['ssi_royalty.ssi_royalty'].create(data)
                                    for pool in lic_prod.license_item_id.item_pool_id.filtered(lambda p: not p.first_sale_date):
                                        pool.update({'first_sale_date': date.today()})

                                        search_pool_rec = self.env['ssi_royalty.pool'].search([('artist_id', '=', royalty.artist_id.id)])
                                        if search_pool_rec:
                                            line_vals = {
                                                'date': date.today(),
                                                'memo': pool.art_id.art_license_number,
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
                                                'memo': pool.art_id.art_license_number,
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

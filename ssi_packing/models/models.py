# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ssi_packing(models.Model):
#     _name = 'ssi_packing.ssi_packing'
#     _description = 'ssi_packing.ssi_packing'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

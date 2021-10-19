from odoo import models, fields, api


class PackingDetail(models.Model):
    _name = 'packing.detail'
    _description = "Packing Detail" 

    is_active = fields.Boolean(string="Is Active")
    picking_id = fields.Many2one('stock.picking', string="Delivery")
    carrier_id = fields.Many2one('delivery.carrier', related='picking_id.carrier_id', string="Carrier")
    tracking_ref = fields.Char(related='picking_id.carrier_tracking_ref', string="Bill Of Landing")
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    partner_id = fields.Many2one('res.partner', string="Customer")
    #this field might needs revisit
    delivery_address = fields.Many2one('res.partner', string="Delivery Address")
    # freight_terms doesnot exist in sale_order model
    # freight_terms = fields.Char(related='sale_id.freight_terms', string="Freight Terms")
    store_number = fields.Char(related='partner_id.store_number', string="Store Number")
    po_number = fields.Char(string="PO Number")
    sequence_number = fields.Integer(string="Number")
    invoice_number = fields.Char(string="Invoice Number")
    dont_ship_before = fields.Date(string="Do Not Ship Before")
    individual_product_cases = fields.Integer(string="Individual Product Cases")
    number_of_carton_ship = fields.Integer(string="Net Number Of Carton with Shipper Labels")
    total_qty_ordered = fields.Integer(string="Total Qty Ordered")
    total_qty_shipped = fields.Integer(string="Total Qty Shipped")
    vendor_number = fields.Char(related='sale_id.vendor_number', string="Vendor Number")
    detail_line = fields.One2many('packing.detail.line', 'packing_id', string="Packing Detail Line")



class PackingDetailLine(models.Model):
    _name = 'packing.detail.line'
    _description = "Packing Detail Line"

    product_id = fields.Many2one('product.product', string="Product")
    sku_lookup_id = fields.Many2one('sku.lookup', string="SKU's Lookup") 
    case_pack = fields.Integer(string="Case Pack")
    carton_number = fields.Integer(string="Carton Number")
    order_qty = fields.Integer(string="Order Qty")
    ship_qty = fields.Integer(string="Ship Qty")
    product_description = fields.Text(related='product_id.description', string="Product Description")
    packing_id = fields.Many2one('packing.detail', string="Packing Detail")


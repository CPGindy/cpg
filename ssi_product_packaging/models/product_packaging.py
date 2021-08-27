import datetime

from odoo import models, fields, api


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    
    #header vals
    partner_id = fields.Many2one('res.partner', string='Customer')
    opportunity_line_id = fields.One2many('crm.lead','product_packaging_id', string='Opportunity')
    product_category = fields.Many2one('product.category', string='Product Category')
    is_active = fields.Boolean(string='Is Active')
    purchase_order_id = fields.One2many('purchase.order','product_packaging_id', string='Purchase Order')
    sale_order_id = fields.One2many('sale.order','product_packaging_id', string='Sale Order')
    status = fields.Selection([('draft', 'Draft'),('production', 'Production'), ('archived', 'Archived')], string='Status')
    mrp_bom_id = fields.One2many('mrp.bom', 'product_packaging_id', string='Bills Of Materials')
    year = fields.Selection(selection='get_years', string='Year', store=True, copy=True)
    date_requested = fields.Date(string='Date Requested')
    quote_need_for = fields.Date(string='Quote Need For')
    anticipated_upload_date = fields.Date(string='Anticipated Upload Date')
    expected_ship_date = fields.Date(string='Expected Ship Date')
    
    #tracking info
    printer = fields.Char(string='Printer')
    factory = fields.Char(string='Factory')
    
    #total print info
    no_quantity = fields.Float(string='# Quantity')
    quantity_per_design = fields.Float(string='Qty Per Design')
    total_quantity = fields.Float(string='Total Quantity')
    per_press_sheet = fields.Float(string='# Per Press Sheet')
    of_press_sheet = fields.Float(string='# Of Press Sheets')
    
    #Card, Listpad or BM
    paper_type = fields.Char(string='Paper Type')
    print = fields.Selection([('x','X'),('y','Y')], string='Print')
    coating = fields.Char(string='Coating')
    special_finish = fields.Char(string='Special Finish')
    ink_on_pen_design = fields.Char(string='Ink On Paper Design')
    glitter_design_count = fields.Integer(string='Glitter Design Count')
    foil_design_count = fields.Integer(string='Foil Design Count')
    folded_dim = fields.Char(string='Folded Dim')
    finished_dimension = fields.Char(string='Finished Dimension')
    card_notes = fields.Char(string='Card Notes')
    comments = fields.Char(string='Comments')
    
    #Envelope Info
    envelope_type = fields.Selection([('type1','Type 1'),('type2','Type 2')], string='Envelope Type')
    envelope_print = fields.Char(string='Envelope Print')
    envelope_coating = fields.Char(string='Envelope Coating')
    envelope_folded_dim = fields.Char(string='Envelope Floaded Bim')
    envelope_flap_shape = fields.Char(string='Envelope Flap Shape')
    envelope_flap_size = fields.Char(string='Envelope Flap Size')
    glue_strip = fields.Char(string='Glue Strip')
    envelope_comments = fields.Char(string='Comments')
    
    #Tray Info
    tray_type = fields.Char(string='Tray Type')
    tray_material = fields.Char(string='Tray Material')
    outer_wrap_material = fields.Char(string='Outer Wrap Material')
    print_warp_xx = fields.Char(string='Print Wrap XX')
    tray_coating = fields.Char(string='Tray Coating')
    tray_dimesions = fields.Char(string='Tray Dimesions')
    tray_comments = fields.Char(string='Comments')
    
    #Lid Type
    lid_type = fields.Selection([('type1','Type 1'),('type2','Type 2')], string='Lid Type')
    lid_material = fields.Char(string='Lid Material')
    lid_print_x = fields.Char(string='Lid Print')
    lid_coating = fields.Char(string='Lid Coating')
    lid_dimensions = fields.Char(string='Lid Dimesion')
    
    #Final Packaging Detail
    cards_per_box = fields.Char(string='Cards Per Box')
    card_banding = fields.Char(string='Card Banding')
    card_packaging = fields.Char(string='Card Packaging')
    envelopes_per_box = fields.Char(string='Envelopes Per Box')
    envelope_banding = fields.Char(string='Envelope Banding')
    box_sealing = fields.Char(string='Box Sealing')
    velcro_magnet = fields.Char(string='Valcro Magnet')
    baker_material = fields.Char(string='Baker Material')
    pads_per_wrap = fields.Char(string='Pads Per Wrap')
    shrink_wrap = fields.Char(string='Shrink Wrap')
    poly_bag = fields.Char(string='Poly Bag')
    listpad_stiker = fields.Char(string='ListPad Sticker')
    listpad_sticker_xx = fields.Char(string='ListPad Sticker')
    
    #Ticketing
    apply_ticket = fields.Char(string='Apply Ticket')
    customer_provided = fields.Char(string='Customer Provided')
    ticket_size = fields.Char(string='Ticket Size')
    
    #General Info
#     carton_pack_qty = fields.Integer(string='Carton Pack Quantity')
    assortment_type = fields.Selection([('type1','Type 1'),('type2','Type 2')], string='Assortment Type')
    qty_each_in_assortment = fields.Integer(string='Quantity Each Assortment')
    general_packing_comments = fields.Char(string='General Packing Comments')
    
    #Cartoon Information
    carton_material = fields.Char(string='Carton Material')
    carton_dimensions = fields.Char(string='Carton Dimensions')
    carton_weight = fields.Float(string='Carton Weight')
    
    
    @api.model
    def get_years(self):
        year_list = []
        now = datetime.datetime.now()
        for i in range(now.year, 1820, -1):
            year_list.append((str(i), str(i)))
        return year_list
    
    
    
    
    

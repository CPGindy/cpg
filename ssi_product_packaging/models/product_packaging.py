import datetime

from odoo import models, fields, api, _


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    
    #Product Specification
    ###################################################################################################
    
    #header vals
    customer_id = fields.Many2one('res.partner', string='Customer')
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
    packaging_type = fields.Many2one('packaging.type', string='Packaging Type')
    sale_order_count = fields.Integer(string='Sale Order', compute='_get_sale_order_count')
    purchase_order_count = fields.Integer(string='Purchase Order', compute='_get_purchase_order_count')
    opportunity_count = fields.Integer(string='Opportunity', compute='_get_opportunity_count')
    bom_count = fields.Integer(string='Bill Of Material', compute='_get_bom_count')
    
    #tracking info Section
    agent = fields.Char(string='Agent')
    factory = fields.Char(string='Factory')
    
    #total print info Section    
    of_packaging_design = fields.Float(string='# Of Packaging Designs')
    of_print_design = fields.Float(string='# Of Print Designs')
    run_length_by_package = fields.Float(string='Run Length by Package')
    total_finished_good_quantity = fields.Float(string='Total Finished Goods Qty')
    print_info_comments = fields.Text(string='Print Comments')
    
    #Card, Listpad or BM Section
    paper_type = fields.Char(string='Paper Type')
    print = fields.Char(string='Print')
    coating = fields.Char(string='Coating')
    special_finish = fields.Char(string='Special Finish')
    ink_on_pen_design = fields.Char(string='Ink On Paper Design')
    glitter_design_count = fields.Integer(string='Glitter Design Count')
    foil_design_count = fields.Integer(string='Foil Design Count')
    folded_dim = fields.Char(string='Folded Dim')
    finished_dimension = fields.Char(string='Finished Dimension')
    card_notes = fields.Char(string='Card Notes')
    comments = fields.Text(string='Comments')
    
    #Envelope Info Section
    envelope_type = fields.Selection([('100_gsm','100 GSM Uncoded Book'),('80_gsm','80 GSM Uncoded Book'),('tbd','TBD')], string='Envelope Type')
    envelope_print = fields.Char(string='Envelope Print')
    envelope_coating = fields.Char(string='Envelope Coating')
    envelope_folded_dim = fields.Char(string='Envelope Folded Dim')
    envelope_flap_shape = fields.Char(string='Envelope Flap Shape')
    envelope_flap_size = fields.Char(string='Envelope Flap Size')
    glue_strip = fields.Char(string='Glue Strip')
    envelope_comments = fields.Text(string='Comments')
    
    #Tray Info Section
    tray_type = fields.Char(string='Tray Type')
    tray_material = fields.Char(string='Tray Material')
    outer_wrap_material = fields.Char(string='Outer Wrap Material')
    print_warp_xx = fields.Char(string='Print Wrap XX')
    tray_coating = fields.Char(string='Tray Coating')
    tray_dimesions = fields.Char(string='Tray Dimesions')
    tray_comments = fields.Text(string='Comments')
    
    #Lid Type Section
    lid_type = fields.Char(string='Lid Type')
    lid_material = fields.Char(string='Lid Material')
    lid_print_x = fields.Char(string='Lid Print X/X')
    lid_coating = fields.Char(string='Lid Coating')
    lid_dimensions = fields.Char(string='Lid Dimension')
    lid_comments = fields.Text(string='Lid Comments')
    
    #Final Packaging Detail Section
    cards_per_box = fields.Char(string='Cards Per Box')
    card_banding = fields.Char(string='Card Banding')
    number_design_per_box = fields.Char(string='# Designs Per Box')
    qty_each_of_design = fields.Float(string='Qty Each Of # Designs')
    card_packing = fields.Text(string='Card Packing')
    envelopes_per_box = fields.Char(string='Envelopes Per Box')
    envelope_banding = fields.Char(string='Envelope Banding')
    box_sealing = fields.Char(string='Box Sealing')
    velcro_magnet_ribbon = fields.Char(string='Valcro/Magnet/Ribbon')
    baker_material = fields.Char(string='Baker Material')
    pads_per_wrap = fields.Char(string='Pads Per Wrap')
    shrink_wrap = fields.Char(string='Shrink Wrap')
    poly_bag = fields.Char(string='Poly Bag')
    listpad_stiker = fields.Selection([('yes','YES'),('no','NO')], string='ListPad Sticker')
    listpad_sticker_xx = fields.Char(string='ListPad Print Sticker', help="X/X")
    
    #Ticketing Section
    apply_ticket = fields.Char(string='Apply Ticket')
    customer_provided = fields.Char(string='Customer Provided')
    ticket_size = fields.Char(string='Ticket Size')
    
    #General Info Section
#     carton_pack_qty = fields.Integer(string='Carton Pack Quantity')
    assortment_type = fields.Selection([('assorted','Assorted'),('solid','Solid')], string='Type')
    qty_each_in_assortment = fields.Integer(string='Quantity Each Assortment')
    general_packing_comments = fields.Text(string='General Packing Comments')
    
    #Cartoon Information
    carton_material = fields.Char(string='Carton Material')
    carton_dimensions = fields.Char(string='Carton Dimensions')
    carton_weight = fields.Float(string='Carton Weight')
    
    #Puzzle Specification
    ###################################################################################################
    
    #Printing Puzzle Section
    puzzle_print = fields.Selection([('box_lid','Box Lid'),('box_bottom','Box Bottom')], string='Print')
    puzzle_print_first = fields.Char(string='Puzzle Printing 1st')
    puzzle_print_first_layer = fields.Char(string='Layer 1')
    puzzle_print_second = fields.Char(string='Puzzle Printing 2nd')
    puzzle_print_second_layer = fields.Char(string='Layer 2')
    poster_printing = fields.Char(string='Poster Printing')
    price_sticker = fields.Char(string='Price Sticker')
    
    #Material Puzzle Section
    puzzle_material = fields.Selection([('box_lid','Box Lid'),('box_bottom','Box Bottom')], string='Material')
    puzzle_material_first = fields.Char(string='Puzzle Material 1st')
    puzzle_material_first_layer = fields.Char(string='Layer 1')
    puzzle_material_second = fields.Char(string='Puzzle Material 2nd')
    puzzle_material_second_layer = fields.Char(string='Layer 2')
    polybag = fields.Char(string='Polybag')
    poster_material = fields.Char(string='Poster Material')
    
    #Binding Puzzle Section
    box_binding = fields.Char(string='Box Binding')
    puzzle_binding = fields.Char(string='Puzzle Binding')
    poster_binding = fields.Char(string='Poster Binding')
    assembly_binding = fields.Char(string='Assembly Binding')
    
    #Extent Section
    extent = fields.Char(string='Extent')
    
    #Size Puzzle Section
    size_box = fields.Char(string='Box')
    size_puzzle = fields.Char(string='Puzzle')
    size_poster = fields.Char(string='Poster')
    size_price_sticker = fields.Char(string='Price Sticker')
    
    #Origination Puzzle Section
    origination = fields.Char(string='Origination')
    
    @api.model
    def get_years(self):
        year_list = []
        now = datetime.datetime.now()
        for i in range(now.year+3, now.year-21, -1):
            year_list.append((str(i), str(i)))
        return year_list
    
    def _get_sale_order_count(self):
        for record in self:
            sale_count = self.env['sale.order'].sudo().search_count([('product_packaging_id', '=', record.id)])
            record.sale_order_count = sale_count
            
    def _get_purchase_order_count(self):
        for record in self:
            purchase_count = self.env['purchase.order'].sudo().search_count([('product_packaging_id', '=', record.id)])
            record.purchase_order_count = purchase_count
            
    def _get_opportunity_count(self):
        for record in self:
            opportunity_count = self.env['crm.lead'].sudo().search_count([('product_packaging_id', '=', record.id)])
            record.opportunity_count = opportunity_count
            
    def _get_bom_count(self):
        for record in self:
            bom_count = self.env['mrp.bom'].sudo().search_count([('product_packaging_id', '=', record.id)])
            record.bom_count = bom_count
            
            
    def action_view_sale(self):
        sale_lines = self.env['sale.order'].search([('product_packaging_id', '=', self.id)])
        sale_ids = []
        for line in sale_lines:
            sale_ids.append(line.id)    
        return {  
            'name': _('Sale Order'),
            'view_mode': 'tree,form', 			
            'search_view_id': [self.env.ref('sale.view_quotation_tree').id],
            'view_type': 'form', 
            'res_model': 'sale.order', 			
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', sale_ids)],
            'target': 'current',
        }
    
    def action_view_purchase(self):
        purchase_lines = self.env['purchase.order'].search([('product_packaging_id', '=', self.id)])
        purchase_ids = []
        for line in purchase_lines:
            purchase_ids.append(line.id)    
        return {  
            'name': _('Purchase Order'), 			
            'search_view_id': self.env.ref('purchase.purchase_order_view_tree').id, 
            'view_mode': 'tree,form',
            'res_model': 'purchase.order', 			
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', purchase_ids)],
            'target': 'current',
        }
    
    def action_view_opportunity(self):
        opportunity_lines = self.env['crm.lead'].search([('product_packaging_id', '=', self.id)])
        opportunity_ids = []
        for line in opportunity_lines:
            opportunity_ids.append(line.id)    
        return {  
            'name': _('Opportunity'),
            'view_mode': 'tree,form', 			
            'search_view_id': self.env.ref('crm.crm_case_tree_view_oppor').id, 			
            'view_type': 'form', 
            'res_model': 'crm.lead', 			
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', opportunity_ids)],
            'target': 'current',
        }
    
    def action_view_bom(self):
        bom_lines = self.env['mrp.bom'].search([('product_packaging_id', '=', self.id)])
        bom_ids = []
        for line in bom_lines:
            bom_ids.append(line.id)    
        return {  
            'name': _('Bills Of Material'),
            'view_mode': 'tree,form', 			
            'search_view_id': self.env.ref('mrp.mrp_bom_tree_view').id, 			
            'view_type': 'form', 
            'res_model': 'mrp.bom', 			
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', bom_ids)],
            'target': 'current',
        }
    
    
    
    
    

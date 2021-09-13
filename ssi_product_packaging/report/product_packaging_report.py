from odoo import models

class ProductPackagingXlsx(models.AbstractModel):
    _name = 'report.ssi_product_packaging.packaging_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Product Packaging')
        format1 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        format2 = workbook.add_format({'font_size': 12, 'align': 'left'})
        format3 = workbook.add_format({'num_format': 'mm/dd/yy','font_size': 12, 'align': 'left'})
        current_column = 0
        while current_column < 69:
            if (current_column == 0 or current_column == 2):
                sheet.set_column(current_column,current_column,32)
            else:
                sheet.set_column(current_column,current_column,20)
            current_column += 1
        
        sheet.write(0,0, 'Customer', format1)
        sheet.write(0,1, 'Product Type', format1)
        sheet.write(0,2, 'Product', format1)
        
        sheet.write(0,3, 'Date Requested', format1)
        sheet.write(0,4, 'Quote Need By', format1)
        
        sheet.write(0,5, 'Agent(Print)', format1)
        sheet.write(0,6, 'Factory', format1)
        
        #Total Print Info
        sheet.write(0,7, '# Of Packaging Info', format1)
        sheet.write(0,8, '# Of Print Designs', format1)
        sheet.write(0,9, 'Run Length By Package', format1)     
        sheet.write(0,10, "Finished Good Qty",format1)       
        sheet.write(0,11, 'Print Comments', format1)
        
        sheet.write(0,12, 'Ant Upload Date', format1)
        sheet.write(0,13, 'Expected Ship Date', format1)
        
        #Card ListPad or BM
        sheet.write(0,14, 'Paper Type', format1)
        sheet.write(0,15, 'Print X/X', format1)
        sheet.write(0,16, 'Coating', format1)
        sheet.write(0,17, 'Special Finish', format1)
        sheet.write(0,18, 'Ink On Pen Design', format1)
        sheet.write(0,19, 'Glitter Design Count', format1)
        sheet.write(0,20, 'Foil Design Count', format1)
        sheet.write(0,21, 'Folded Dim', format1)
        sheet.write(0,22, 'Finished Dimensions', format1)
        sheet.write(0,23, 'Card Notes', format1)
        sheet.write(0,24, 'Card Comments', format1)
        
        #Envelope Info
        sheet.write(0,25, 'Envelope Type', format1)
        sheet.write(0,26, 'Envelope Print', format1)     
        sheet.write(0,27, "Envelope Coating",format1)       
        sheet.write(0,28, 'Envelope Folded Dim', format1)
        sheet.write(0,29, 'Envelope Flap Shape', format1)
        sheet.write(0,30, 'Envelope Flap Size', format1)
        sheet.write(0,31, 'Glue Strip', format1)
        sheet.write(0,32, 'Envelope Comments', format1)
        
        #Tray Info
        sheet.write(0,33, 'Tray Type', format1)
        sheet.write(0,34, 'Tray Material', format1)
        sheet.write(0,35, 'Out Wrap Mat', format1)     
        sheet.write(0,36, "Print Wrap XX",format1)       
        sheet.write(0,37, 'Tray Coating', format1)
        sheet.write(0,38, 'Tray Dimesions', format1)
        sheet.write(0,39, 'Tray Comments', format1)
        
        #Lid Info
        sheet.write(0,40, 'Lid Type', format1)
        sheet.write(0,41, 'Lid Material', format1)
        sheet.write(0,42, 'Lid Print', format1)
        sheet.write(0,43, 'Lid Coating', format1)
        sheet.write(0,44, 'Lid Dimension', format1)     
        sheet.write(0,45, "Lid Comments",format1) 
        
        #Final Packaging Info
        sheet.write(0,46, 'Cards Per Box', format1)
        sheet.write(0,47, 'Card Banding', format1)
        sheet.write(0,48, 'Card Packing', format1)
        sheet.write(0,49, 'Envelopes Per Box', format1)
        sheet.write(0,50, 'Envelope Banding', format1)
        sheet.write(0,51, 'Box Sealing', format1)
        sheet.write(0,52, 'Velcro/Magnet/Ribbon', format1)
        sheet.write(0,53, 'Baker Material', format1)     
        sheet.write(0,54, "Pads Per Wrap",format1)
        sheet.write(0,55, 'Shrink Wrap', format1)
        sheet.write(0,56, 'Poly Bag', format1)
        sheet.write(0,57, 'ListPad Sticker', format1)     
        sheet.write(0,58, "ListPadPad Sticker X/X",format1)
        
        #Ticketing Info
        sheet.write(0,59, 'Apply Ticket', format1)
        sheet.write(0,60, 'Customer Provided', format1)
        sheet.write(0,61, 'Ticket Size', format1)
        
        #General Packaging Info
        sheet.write(0,62, 'Carton Pack Qty', format1)
        sheet.write(0,63, 'Type', format1)     
        sheet.write(0,64, 'Qty Each Assortment', format1)
        sheet.write(0,65, 'General Packaging Comments', format1)
        
        #Carton Info
        sheet.write(0,66, 'Carton Material', format1)
        sheet.write(0,67, 'Carton Dimensions', format1)     
        sheet.write(0,68, "Carton Weight",format1) 
        
        for index, line in enumerate(lines):
            sheet.write(index+1, 0, line.customer_id.name, format2)
            sheet.write(index+1, 1, line.product_category.name, format2)
            sheet.write(index+1, 2, line.product_id.name, format2)
            
            sheet.write(index+1, 3, line.date_requested, format3)
            sheet.write(index+1, 4, line.quote_need_for, format3)
            
            sheet.write(index+1, 5, line.agent, format2)
            sheet.write(index+1, 6, line.factory, format2)  
            
            sheet.write(index+1, 7, line.of_packaging_design, format2)
            sheet.write(index+1, 8, line.of_print_design, format2)
            sheet.write(index+1, 9, line.run_length_by_package, format2)
            sheet.write(index+1, 10, line.total_finished_good_quantity, format2)   
            sheet.write(index+1, 11, line.print_info_comments, format2)
            
            sheet.write(index+1, 12, line.anticipated_upload_date, format3)
            sheet.write(index+1, 13, line.expected_ship_date, format3)
            
            sheet.write(index+1, 14, line.paper_type, format2)
            sheet.write(index+1, 15, line.print, format2)
            sheet.write(index+1, 16, line.coating, format2)
            sheet.write(index+1, 17, line.special_finish, format2)
            sheet.write(index+1, 18, line.ink_on_pen_design, format2)
            sheet.write(index+1, 19, line.glitter_design_count, format2)
            sheet.write(index+1, 20, line.foil_design_count, format2)
            sheet.write(index+1, 21, line.folded_dim, format2)
            sheet.write(index+1, 22, line.finished_dimension, format2)
            sheet.write(index+1, 23, line.card_notes, format2)
            sheet.write(index+1, 24, line.comments, format2)
            
            sheet.write(index+1, 25, line.envelope_type, format2)
            sheet.write(index+1, 26, line.envelope_print, format2)
            sheet.write(index+1, 27, line.envelope_coating, format2)
            sheet.write(index+1, 28, line.envelope_folded_dim, format2)
            sheet.write(index+1, 29, line.envelope_flap_shape, format2)
            sheet.write(index+1, 30, line.envelope_flap_size, format2)
            sheet.write(index+1, 31, line.glue_strip, format2)
            sheet.write(index+1, 32, line.envelope_comments, format2)
        
            sheet.write(index+1, 33, line.tray_type, format2)
            sheet.write(index+1, 34, line.tray_material, format2)
            sheet.write(index+1, 35, line.outer_wrap_material, format2)
            sheet.write(index+1, 36, line.print_warp_xx, format2)
            sheet.write(index+1, 37, line.tray_coating, format2)
            sheet.write(index+1, 38, line.tray_dimesions, format2)
            sheet.write(index+1, 39, line.tray_comments, format2)

            sheet.write(index+1, 40, line.lid_type, format2)
            sheet.write(index+1, 41, line.lid_material, format2)
            sheet.write(index+1, 42, line.lid_print_x, format2)
            sheet.write(index+1, 43, line.lid_coating, format2)
            sheet.write(index+1, 44, line.lid_dimensions, format2)
            sheet.write(index+1, 45, line.lid_comments, format2)

            sheet.write(index+1, 46, line.cards_per_box, format2)
            sheet.write(index+1, 47, line.card_banding, format2)
            sheet.write(index+1, 48, line.card_packing, format2)
            sheet.write(index+1, 49, line.envelopes_per_box, format2)
            sheet.write(index+1, 50, line.envelope_banding, format2)
            sheet.write(index+1, 51, line.box_sealing, format2)
            sheet.write(index+1, 52, line.velcro_magnet_ribbon, format2)
            sheet.write(index+1, 53, line.baker_material, format2)
            sheet.write(index+1, 54, line.pads_per_wrap, format2)
            sheet.write(index+1, 55, line.shrink_wrap, format2)
            sheet.write(index+1, 56, line.poly_bag, format2)
            sheet.write(index+1, 57, line.listpad_stiker, format2)
            sheet.write(index+1, 58, line.listpad_sticker_xx, format2)
        
            sheet.write(index+1, 59, line.apply_ticket, format2)
            sheet.write(index+1, 60, line.customer_provided, format2)
            sheet.write(index+1, 61, line.ticket_size, format2)
            sheet.write(index+1, 62, line.qty, format2)
            sheet.write(index+1, 63, line.assortment_type, format2)
            sheet.write(index+1, 64, line.qty_each_in_assortment, format2)
            sheet.write(index+1, 65, line.general_packing_comments, format2)
            sheet.write(index+1, 66, line.carton_material, format2)
            sheet.write(index+1, 67, line.carton_dimensions, format2)
            sheet.write(index+1, 68, line.carton_weight, format2)
        
        

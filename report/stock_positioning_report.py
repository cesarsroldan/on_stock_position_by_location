# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
import base64
import xlwt
from odoo.tools.misc import ustr
from time import gmtime, strftime


class StockPositioningReport(models.TransientModel):
    _name = "stock.positioning.report"

    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Report File Name', size=64, readonly=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def print_stock_positioning_pdf(self):
        return self.env.ref('stock_position_by_location.stock_positioning_variant_report_id_x').report_action(self, config=False)

    def get_date_x(self):
        return strftime("%m-%d-%Y %H:%M:%S", gmtime())

    def get_total_qty_x(self):
        qty_list = []
        total_qty_available = 0
        total_incoming_qty = 0
        total_outgoing_qty = 0
        total_virtual_available = 0
        for line in self.stock_positioning_x:
            total_qty_available += line.qty_available
            total_incoming_qty += line.incoming_qty
            total_outgoing_qty += line.outgoing_qty
            total_virtual_available += line.virtual_available
        qty_list.append({
            'total_qty_available': total_qty_available,
            'total_incoming_qty': total_incoming_qty,
            'total_outgoing_qty': total_outgoing_qty,
            'total_virtual_available': total_virtual_available,
        })
        return qty_list

    def print_stock_positioning_xls(self):
        filename = 'Stock Position By Location Report.xlsx'
        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        style_center = xlwt.easyxf(
            'align:vertical center, horizontal center; font:bold on; pattern: pattern solid, fore_colour gray25; border: top thin, bottom thin, right thin, left thin;')
        style_company_name = xlwt.easyxf(
            'font:height 240, bold on; align:vertical center; border: top thin, bottom thin, right thin, left thin;')
        style_title = xlwt.easyxf(
            'font:height 300, bold on; align:horizontal center, vertical center; pattern: pattern solid, fore_color white; border: top thin, bottom thin, right thin, left thin; ')
        style_product = xlwt.easyxf(
            'font:height 240, bold on; align:vertical center; border: top thin, bottom thin, right thin, left thin;')
        style_total_qty = xlwt.easyxf(
            'align: horiz right; font:bold on; pattern: pattern solid, fore_colour gray25; border: top thin, bottom thin, right thin, left thin;')
        style_left = xlwt.easyxf(
            'font:bold on; pattern: pattern solid, fore_colour gray25; border: top thin, bottom thin, right thin, left thin;')
        style_border = xlwt.easyxf(
            'border: top thin, bottom thin, right thin, left thin; align:vertical center, horizontal center;')
        font_red = xlwt.easyxf(
            'font: color red; border: top thin, bottom thin, right thin, left thin; align:vertical center, horizontal center;')
        style_border_left = xlwt.easyxf('border: top thin, bottom thin, right thin, left thin;')
        style_bold = xlwt.easyxf(
            'font:bold on; border: top thin, bottom thin, right thin, left thin; align:vertical center, horizontal center;')
        font_red_bold = xlwt.easyxf(
            'font: color red, bold on; border: top thin, bottom thin, right thin, left thin; align:vertical center, horizontal center;')

        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        style.font = font
        worksheet = workbook.add_sheet('Sheet 1')

        user_obj = self.env['res.users'].sudo().browse(self._uid)
        company_name = 'Company Name : ' + user_obj.company_id.name
        worksheet.write_merge(0, 0, 0, 0, ustr(company_name), style_company_name)
        worksheet.write_merge(1, 2, 1, 3, 'Stock Positioning Report', style_title)
        worksheet.write(3, 0, ustr(self.name_get()[0][1]), style_product)
        worksheet.write(4, 0, 'Date : ' + strftime("%m-%d-%Y %H:%M:%S", gmtime()), xlwt.easyxf('font: bold on;'))

        total_qty_available = 0
        total_incoming_qty = 0
        total_outgoing_qty = 0
        total_virtual_available = 0
        row = 5
        col = 0
        worksheet.write(row, col, 'Location', style_left)
        worksheet.col(col).width = 256 * 35
        col += 1
        worksheet.write(row, col, 'On Hand QTY', style_center)
        worksheet.col(col).width = 256 * 15
        col += 1
        worksheet.write(row, col, 'Incoming QTY', style_center)
        worksheet.col(col).width = 256 * 15
        col += 1
        worksheet.write(row, col, 'Outgoing QTY', style_center)
        worksheet.col(col).width = 256 * 15
        col += 1
        worksheet.write(row, col, 'Forecast QTY', style_center)
        worksheet.col(col).width = 256 * 15
        row += 1
        for line in self.stock_positioning_x:
            if line.qty_available or line.virtual_available:
                col = 0
                # LOCATION
                location = line.location_id.name_get()[0][1]
                worksheet.write(row, col, location, style_border_left)
                col += 1

                total_qty_available += line.qty_available
                # On Hand QTY
                if line.qty_available:
                    if line.qty_available < 0.00:
                        worksheet.write(row, col, "{0:.2f}".format(line.qty_available),
                                        font_red)
                    else:
                        worksheet.write(row, col, "{0:.2f}".format(line.qty_available),
                                        style_border)
                else:
                    worksheet.write(row, col, "{0:.2f}".format(line.qty_available),
                                    style_border)
                col += 1
                total_incoming_qty += line.incoming_qty
                # Incoming QTY
                if line.incoming_qty:
                    if line.incoming_qty < 0:
                        worksheet.write(row, col, "{0:.2f}".format(line.incoming_qty),
                                        font_red)
                    else:
                        worksheet.write(row, col, "{0:.2f}".format(line.incoming_qty),
                                        style_border)
                else:
                    worksheet.write(row, col, "{0:.2f}".format(line.incoming_qty),
                                    style_border)

                col += 1
                total_outgoing_qty += line.outgoing_qty
                # Outgoing QTY
                if line.outgoing_qty:
                    if line.outgoing_qty < 0:
                        worksheet.write(row, col, "{0:.2f}".format(line.outgoing_qty),
                                        font_red)
                    else:
                        worksheet.write(row, col, "{0:.2f}".format(line.outgoing_qty),
                                        style_border)
                else:
                    worksheet.write(row, col, "{0:.2f}".format(line.outgoing_qty),
                                    style_border)

                col += 1
                total_virtual_available += line.virtual_available
                # Forecast QTY
                if line.virtual_available:
                    if line.virtual_available < 0:
                        worksheet.write(row, col, "{0:.2f}".format(line.virtual_available),
                                        font_red)
                    else:
                        worksheet.write(row, col, "{0:.2f}".format(line.virtual_available),
                                        style_border)
                else:
                    worksheet.write(row, col, "{0:.2f}".format(line.virtual_available),
                                    style_border)
                row += 1
        # TOTAL OF
        col = 0
        worksheet.write(row, col, 'Total Qty', style_total_qty)
        col += 1
        # TOTAL On Hand QTY
        if total_qty_available < 0:
            worksheet.write(row, col, "{0:.2f}".format(total_qty_available), font_red_bold)
        else:
            worksheet.write(row, col, "{0:.2f}".format(total_qty_available), style_bold)
        col += 1
        # TOTAL Incoming QTY
        if total_incoming_qty < 0:
            worksheet.write(row, col, "{0:.2f}".format(total_incoming_qty), font_red_bold)
        else:
            worksheet.write(row, col, "{0:.2f}".format(total_incoming_qty), style_bold)
        col += 1
        # TOTAL Outgoing QTY
        if total_outgoing_qty < 0:
            worksheet.write(row, col, "{0:.2f}".format(total_outgoing_qty), font_red_bold)
        else:
            worksheet.write(row, col, "{0:.2f}".format(total_outgoing_qty), style_bold)
        col += 1
        # TOTAL Forecast QTY
        if total_virtual_available < 0:
            worksheet.write(row, col, "{0:.2f}".format(total_virtual_available), font_red_bold)
        else:
            worksheet.write(row, col, "{0:.2f}".format(total_virtual_available), style_bold)
        row += 2

        workbook.save(filename)
        file = open(filename, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
        export_obj = self.env['stock.positioning.report'].create({'excel_file': out,'file_name': filename})

        return {
            'view_mode': 'form',
            'res_id': export_obj.id,
            'res_model': 'stock.positioning.report',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    stock_positioning_x = fields.One2many('stock.positioning.x', 'product_variant_id', string="Stocks Positioning",)

    def _get_stock_positioning_data_x(self):
        #print("\n_get_stock_positioning_data_x()....")
        
        StockLocation = self.env['stock.location']
        StockMove = self.env['stock.move']
        StockQuant = self.env['stock.quant']

        location_objs = StockLocation.search([('usage', '=', 'internal')])

        for location_obj in location_objs:
            for rec in self:
                if rec.type == 'service':
                    continue
                if rec.id:
                    self._cr.execute("DELETE FROM stock_positioning_x WHERE product_variant_id=%s AND location_id=%s", (rec.id,location_obj.id))
                product_and_qty_in = dict((item['product_id'][0], item['product_qty']) for item in StockMove.read_group([('state', 'not in', ('done', 'cancel', 'draft')),('product_id', '=', rec.id), ('location_dest_id', '=', location_obj.id)], ['product_id', 'product_qty'], ['product_id']))
                product_and_qty_out = dict((item['product_id'][0], item['product_qty']) for item in StockMove.read_group([('state', 'not in', ('done', 'cancel', 'draft')), ('product_id', '=', rec.id), ('location_id', '=', location_obj.id)], ['product_id', 'product_qty'], ['product_id']))
                product_and_qty_on_hand = dict((item['product_id'][0], item['quantity']) for item in StockQuant.read_group([('product_id', '=', rec.id), ('location_id', '=', location_obj.id)], ['product_id', 'quantity'], ['product_id']))
                if product_and_qty_on_hand.get(rec.id) or product_and_qty_in.get(rec.id) or product_and_qty_out.get(rec.id):
                    rec.stock_positioning_x |= self.env['stock.positioning.x'].create({
                        'location_id': location_obj.id,
                        'qty_available': product_and_qty_on_hand.get(rec.id, 0.0),
                        'incoming_qty': product_and_qty_in.get(rec.id, 0.0),
                        'outgoing_qty': product_and_qty_out.get(rec.id, 0.0),
                        'product_variant_id': rec.id,
                        'virtual_available': (product_and_qty_on_hand.get(rec.id, 0.0)) + (product_and_qty_in.get(rec.id, 0.0) - product_and_qty_out.get(rec.id, 0.0))})


    def open_stock_positioning(self):
        stock_positioning_obj = self.env['stock.positioning.x'].search(
            [('product_variant_id', '=', self.id)])
        return {
            'name': _('Stock Positioning By Location'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.positioning.x',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', stock_positioning_obj.ids)],
        }


class stock_positioning_x(models.Model):
    _name = 'stock.positioning.x'

    location_id = fields.Many2one('stock.location', string="Ubicacion")
    qty_available = fields.Float('A mano')
    incoming_qty = fields.Float('En Transito')
    outgoing_qty = fields.Float('Reservado')
    virtual_available = fields.Float('Disponible')
    product_variant_id = fields.Many2one('product.product', 'Producto')

    @api.model
    def action_product_stock_by_location(self):
        stock_by_location = []
        ctx = dict(self.env.context or {})
        product_ids = self.env['product.product'].sudo().search([('active', '=', True), ('type', '=', 'product')])
        quant_ids = self.get_stock_by_location(products=product_ids)
        return {
            'name': _('Reporte de Inventario'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.positioning.x',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', quant_ids)],
            'context': ctx,
        }

    def get_stock_by_location(self, products=None):
        StockLocation = self.env['stock.location']
        StockMove = self.env['stock.move']
        StockQuant = self.env['stock.quant']
        location_objs = StockLocation.sudo().search([('usage', '=', 'internal'), ('company_id', 'in', self.env.company.ids)])
        quant_ids = []
        for location_obj in location_objs:
            for rec in products:
                #Busco las cantidades reservadas, en transito y a mano
                product_and_qty_in = dict((item['product_id'][0], item['product_qty']) for item in StockMove.sudo().read_group([('state', 'not in', ('done', 'cancel', 'draft')),('product_id', '=', rec.id), ('location_dest_id', '=', location_obj.id), ('company_id', 'in', self.env.company.ids)], ['picking_id', 'product_id', 'product_qty'], ['product_id']))
                product_and_qty_out = dict((item['product_id'][0], item['product_qty']) for item in StockMove.sudo().read_group([('state', 'not in', ('done', 'cancel', 'draft')), ('product_id', '=', rec.id), ('location_id', '=', location_obj.id), ('company_id', 'in', self.env.company.ids)], ['picking_id', 'product_id', 'product_qty'], ['product_id']))
                product_and_qty_on_hand = dict((item['product_id'][0], item['quantity']) for item in StockQuant.sudo().read_group([('product_id', '=', rec.id), ('location_id', '=', location_obj.id), ('company_id', 'in', self.env.company.ids)], ['product_id', 'quantity'], ['product_id']))
                #Hago search para ver si existe linea con el mismo producto y ubicacion
                product_ids = self.env['stock.positioning.x'].sudo().search([('product_variant_id', '=', rec.id), ('location_id', '=', location_obj.id)])
                if product_ids:
                    for p_id in product_ids:
                        if product_and_qty_on_hand.get(rec.id) or product_and_qty_in.get(rec.id) or product_and_qty_out.get(rec.id):
                            p_id.sudo().write({
                                'qty_available': product_and_qty_on_hand.get(rec.id, 0.0),
                                'incoming_qty': product_and_qty_in.get(rec.id, 0.0),
                                'outgoing_qty': product_and_qty_out.get(rec.id, 0.0),
                                'virtual_available': (product_and_qty_on_hand.get(rec.id, 0.0)) + (product_and_qty_in.get(rec.id, 0.0) - product_and_qty_out.get(rec.id, 0.0))
                            })
                        quant_ids.append(p_id.id)
                else:
                    if product_and_qty_on_hand.get(rec.id) or product_and_qty_in.get(rec.id) or product_and_qty_out.get(rec.id):
                        quant_id = self.env['stock.positioning.x'].sudo().create({
                            'location_id': location_obj.id,
                            'qty_available': product_and_qty_on_hand.get(rec.id, 0.0),
                            'incoming_qty': product_and_qty_in.get(rec.id, 0.0),
                            'outgoing_qty': product_and_qty_out.get(rec.id, 0.0),
                            'product_variant_id': rec.id,
                            'virtual_available': (product_and_qty_on_hand.get(rec.id, 0.0)) + (product_and_qty_in.get(rec.id, 0.0) - product_and_qty_out.get(rec.id, 0.0))})
                        quant_ids.append(quant_id.id)
        return quant_ids

stock_positioning_x()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

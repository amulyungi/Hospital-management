from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class KnowYourCustomerWizard(models.TransientModel):
    _name='know.your.customer.wizard'
    _description = 'Know Your Customer Wizard'

    search_param = fields.Char(string="Search")
    partner_id = fields.Many2one('res.partner', string='Partner')
    kyc_ids = fields.Many2many('know.your.customer', string='KYC')
    id_type = fields.Selection(
        [
            ('NATIONAL_ID', 'National ID'), 
            ('ALIEN_CARD', 'Alien ID'),
            ('PASSPORT', 'Passport')
        ], string='ID Type', default='NATIONAL_ID')
    search_mode = fields.Selection(
        [
            ('basic_search', 'Basic search'), 
            ('advanced_search', 'Advanced search')
        ], string='Search Mode', default='basic_search')

    def set_the_default_country(self):
        return self.env['res.country'].sudo().search([('name', '=', 'Kenya')], limit=1).id
            
    country_id = fields.Many2one('res.country', string='Country', default=set_the_default_country)        

    @api.onchange('search_mode')
    def onchange_search_mode(self):
        """ Automatically updates the search_param attribute depending on the search mode value"""

        selected_mode = dict(self._fields['search_mode'].selection).get(self.search_mode)

        if selected_mode == "Basic search":
            self.search_param = ""
        else:
            self.search_param = self.partner_id.name            

    def search_kyc_data_from_odoo_or_smile_id(self, search_param):
        if search_param:                        
            if self.search_mode == "advanced_search" or self.search_mode == False:
                # Search KYC data from Odoo
                kyc_data = self.env['know.your.customer'].sudo().search(
                    [
                        '|',
                        ('full_name','=', search_param),
                        ('id_number','=', search_param)
                    ]
                )

                return kyc_data
            else:
                # Search KYC data from Smile ID
                country_id = self.country_id.id
                _country = self.env['res.country'].sudo().search([('id', '=', country_id)], limit=1)
                kyc_data = self.env['know.your.customer'].sudo().get_kyc_data_as_tuple(search_param, self.id_type, _country.code)

                return kyc_data        
        else:
            raise ValidationError("You must provide either the ID number, passport number or full names")

    def search_kyc_data(self):
        recs = []
        kyc_data = self.search_kyc_data_from_odoo_or_smile_id(self.search_param)
        
        if kyc_data:
            for r in kyc_data:
                recs.append(r.id)

        action = {
            "name": "Know Your Customer(KYC)",
            "type": "ir.actions.act_window",
            "res_model": "know.your.customer.wizard",
            "domain": [],
            "view_mode": "form",
            "view_id": False,
            "nodestroy": True,
            "target": "new",
            "context": {
                'default_search_param': self.search_param,
                'default_partner_id': self.partner_id.id,
                'default_kyc_ids': recs
            }
        } 

        return action

    def match_kyc_data(self):
        kyc = self.kyc_ids
        if len(self.kyc_ids) == 1:
            partner = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
            kyc_data = self.env['know.your.customer'].sudo().search([('id','=', kyc.id)])

            partner.write({'kyc_id': kyc.id, 'id_number': kyc_data.id_number})
        else:
            raise ValidationError("Kindly ensure you select only one record")

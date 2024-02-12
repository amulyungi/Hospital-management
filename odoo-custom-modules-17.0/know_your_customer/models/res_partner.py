from email import message
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartnerCustom(models.Model):
    _inherit = "res.partner"


    kyc_id = fields.Many2one('know.your.customer', string="KYC Details", tracking=True)
    

    def action_verify_kyc_details(self):
        """Returns the KYC wizard"""

        recs = []
        kyc_data = self.get_kyc_details()

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
                'default_search_param': self.name,
                'default_partner_id': self.id,
                'default_kyc_ids': recs
            }
        }
        
        return action

    def get_kyc_details(self):
        return self.env['know.your.customer.wizard'].sudo().search_kyc_data_from_odoo_or_smile_id(self.name)             
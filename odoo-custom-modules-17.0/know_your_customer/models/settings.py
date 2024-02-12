from odoo import api, fields, models, _


class SmileIdentitySettings(models.TransientModel):
    _inherit = 'res.config.settings'

    smile_identity_base_url = fields.Char(string = "Smile Identity Base URL")
    smile_identity_partner_id = fields.Char(string = "Smile Identity Partner Id")
    smile_identity_api_key = fields.Char(string = "Smile Identity API Key")
    smile_identity_header = fields.Char(string = "Smile Identity Header")
    smile_identity_timezone = fields.Char(string = "Smile Identity Timezone")

    def set_values(self):
        res = super(SmileIdentitySettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param('smile_identity.smile_identity_base_url', self.smile_identity_base_url)
        self.env['ir.config_parameter'].sudo().set_param('smile_identity.smile_identity_partner_id', self.smile_identity_partner_id)
        self.env['ir.config_parameter'].sudo().set_param('smile_identity.smile_identity_api_key', self.smile_identity_api_key)
        self.env['ir.config_parameter'].sudo().set_param('smile_identity.smile_identity_header', self.smile_identity_header)
        self.env['ir.config_parameter'].sudo().set_param('smile_identity.smile_identity_timezone', self.smile_identity_timezone)
        
        return res

    @api.model
    def get_values(self):
        res = super(SmileIdentitySettings, self).get_values()
        base_url = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_base_url')
        partner_id = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_partner_id')
        api_key = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_api_key')
        header = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_header')
        timezone = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_timezone')
        res.update(
            { 
                'smile_identity_base_url': base_url,
                'smile_identity_partner_id': partner_id,
                'smile_identity_api_key': api_key,
                'smile_identity_header': header,
                'smile_identity_timezone': timezone
            }
        )

        return res            
    
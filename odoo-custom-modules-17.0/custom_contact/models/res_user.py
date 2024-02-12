import contextlib
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.addons.auth_signup.models.res_partner import now
from odoo.tools import email_normalize


_logger = logging.getLogger(__name__)


class CustomResUser(models.Model):
    _inherit = "res.users"
    
    def create_user(self, partner, data):
        """Create the User based on their Partner details"""
        
        try:
            if partner and data:            
                admin = self.env['res.users'].sudo().search([('id','=',2)])        
                portal_group = self.env['res.groups'].sudo().search([('id','=',10)])
                partner = self.env['res.partner'].sudo().search([('id','=',partner.id)])                
                        
                user_details = {
                    "lang": "en_US",
                    "login": partner.email,
                    "partner_id": partner.id,
                    "groups_id": [portal_group.id],
                    "password": data.get("password"),
                    "company_id": partner.company_id.id,
                    'company_ids': [(6, 0, [partner.company_id.id])]
                }
                
                user = self.env['res.users'].with_user(admin).create(user_details)
                return user
        except Exception as e:
            return e
        
    def reset_password(self, login):
        """ retrieve the user corresponding to login (login or email),
            and reset their password
        """
        users = self.search(self._get_login_domain(login))
        if not users:
            users = self.search(self._get_email_domain(login))
        if not users:
            raise Exception(_('No account found for this login'))
        if len(users) > 1:
            raise Exception(_('Multiple accounts found for this login'))
        return users.action_reset_password()

    def action_reset_password(self):
        try:
            return self._action_reset_password()
        except MailDeliveryException as mde:
            if len(mde.args) == 2 and isinstance(mde.args[1], ConnectionRefusedError):
                raise UserError(_("Could not contact the mail server, please check your outgoing email server configuration")) from mde
            else:
                raise UserError(_("There was an error when trying to deliver your Email, please check your configuration")) from mde
                
    def _action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode') or self.env.context.get('import_file'):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        base_url = self.env['ir.config_parameter'].sudo().get_param('app_1_base_url')
        
        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))            
            
            if base_url and user.partner_id.signup_valid: 
                # Generate the password reset link
                generate_password_reset_link = base_url + "/authentication/reset-password?token=" + user.partner_id.signup_token
                user.partner_id.write({'reset_password_url': generate_password_reset_link})             
            
                # Fetch email template
                email_template = self.env['mail.template'].sudo().search(
                    [
                        ('name', '=', 'Password Reset Notification(Customized)')
                    ], limit=1
                )

                if email_template:
                    # Send the email notification
                    email_template.sudo().send_mail(user.id, force_send=True, raise_exception=True)                
                    _logger.info(f"A password reset email has been sent to {user.email}")                    

    def get_app_1_base_url(self):
        """ Returns the base URL for app no. 1
        """
        if len(self) > 1:
            raise ValueError("Expected singleton or no record: %s" % self)
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('app_1_base_url')    
        return base_url
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomResPartner(models.Model):
    _inherit = "res.partner"
    
    
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("dont_reveal_gender", "I Prefer Not To Reveal My Gender"),            
        ], string="Gender")
    id_number = fields.Char(string="ID Number")
    phone_number_verification_status = fields.Selection(
        [
            ("unverified", "Unverified"),
            ("verified", "Verified")           
        ], string="Phone No. Verification Status", default="unverified")
    email_verification_status = fields.Selection(
        [
            ("unverified", "Unverified"),
            ("verified", "Verified")           
        ], string="Email Verification Status", default="unverified")
    id_number_verification_status = fields.Selection(
        [
            ("unverified", "Unverified"),
            ("verified", "Verified")           
        ], string="ID Verification Status", default="unverified")
    
    reset_password_url = fields.Char(string='Reset Password URL')                
    
    def create_partner(self, data):
        """Create the Partner"""
        
        try:
            admin = self.env["res.users"].sudo().search([("id","=",2)])
            partner_category = self.env["res.partner.category"].search(
                [
                    ("name", "=", "Customer")
                ], limit=1)
            
            partner_details = {
                "name": (data.get("first_name") + " " + data.get("last_name")).title(),
                "first_name": (data.get("first_name")).capitalize(),
                "last_name": (data.get("last_name")).capitalize(),
                "gender": data.get("gender"),
                "phone": data.get("phone"),
                "email": data.get("email"),
                "country_id": data.get("country"),
                "company_type": "person", 
                "category_id": partner_category,
                "company_id": admin.company_id.id        
            }
            
            partner = self.env["res.partner"].with_user(admin).create(partner_details)
            return partner
        except Exception as e:
            return e
                
    def get_partner_profile(self, partner_id):
        """Get Partner details using the partner id"""        
        
        try:
            response_data = dict()        
            partner = self.env["res.partner"].search([("id", "=", partner_id)])

            if partner:
                response_data["partner_id"] = partner.id
                response_data["partner_name"] = partner.name
                response_data["phone"] = partner.phone   
                response_data["email"] = partner.email
                response_data["total_invoiced_amount"] = partner.total_invoiced
                response_data["total_amount_due"] = partner.payment_amount_due #This is labeled as `Invoiced` on the UI

            return response_data
        except Exception as e:
            return e             
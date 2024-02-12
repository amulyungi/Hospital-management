# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response, Request
import json
import logging

logger = logging.getLogger(__name__)


class CustomContact(http.Controller):
    @http.route('/api/v1/partner', methods=['GET'], auth='user', type='http')
    def get_partner_profile(self, **kw):
        """Get the Partner details"""
        
        partner_id = int(request.params.get('id'))
        headers = {'Content-Type': 'application/json'}        

        try:
            partner = request.env['res.partner'].sudo().get_partner_profile(partner_id)
            if partner:
                partner["message"] = "Success"
                return partner
            else:
                return {"error": "Not Found"}
        except Exception as e:
            return {"error": e}
            
    @http.route('/api/v1/partner', methods=['POST'], auth='public', type='json')
    def create_partner_and_user(self, **kw):
        """Sign up the user by creating res.partner and res.users records"""
                          
        response_data = dict()
        try:
            data = json.loads(request.httprequest.data)
            headers = {'Content-Type': 'application/json'}            
            
            admin = request.env['res.users'].sudo().search([('id','=',2)])
            partner = request.env['res.partner'].with_user(admin).create_partner(data)
            
            if partner:
                response_data["partner_id"] = partner.id
                response_data["message"] = "Partial Success"
                status_code = 207
            
                # Create user
                user = request.env['res.users'].with_user(admin).create_user(partner, data)
                
                if user:
                    response_data["user_id"] = user.id
                    response_data["message"] = "Success"
                    status_code = 200                    
                
            return response_data
        except Exception as e:
            return {"error": e}
        
    @http.route('/api/v1/forgot_password', methods=['POST'], auth='public', type='json')
    def generate_auth_token(self, **kw):
        """Generates an auth token and a password reset link.
        It also sends a password reset email to the user"""
                          
        response_data = dict()
        headers = {'Content-Type': 'application/json'}
        status = 200 
        
        try:
            data = json.loads(request.httprequest.data)
            email = data.get("email")
            user = request.env['res.users'].sudo().reset_password(email)
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)                            
            
            if partner:
                response_data["message"] = "Please check your email for the password reset link"
            else:
                response_data["message"] = "Ooops! The email you provided does not exist." 
                
            return response_data
        except Exception as e:
            return {"error": e}        

    @http.route('/api/v1/reset_password', methods=['POST'], auth='public', type='json')
    def reset_user_password(self, **kw):
        """Reset the user password"""
                          
        headers = {'Content-Type': 'application/json'} 
        try:
            data = json.loads(request.httprequest.data)
            token = data.get('token')
            confirm_password = data.get('confirm_password')
            new_password = data.get('new_password')
            
            # Find the partner corresponding to a token
            partner = request.env['res.partner'].sudo()._signup_retrieve_partner(token, check_validity=True)
                            
            if not partner:
                return {"error": "Invalid token!"}
            
            if not confirm_password or not new_password:
                return {"error": "Password is required!"}                
            
            if confirm_password != new_password:
                return {"error": "Passwords don't match!"}
            
            # Find the user based on their email and update their new password
            user = request.env['res.users'].sudo().search([('login','=', partner.email)])
            if user:
                user.write({'password': new_password})
            
            # Invalidate/Remove the token
            partner.write(
                {
                    'signup_token': False,
                    'signup_type': False,
                    'signup_expiration': False,
                    'reset_password_url': False
                }
            )
            
            return {
                "message": "Password was reset successfully"
            }
        except Exception as e:
            return {"error": e}
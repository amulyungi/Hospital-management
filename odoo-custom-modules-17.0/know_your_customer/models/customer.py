import base64
import hashlib
import hmac
import json
import requests
import logging
import pytz

from odoo import models, fields, api, _
from datetime import datetime
from odoo.http import Response
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class KnowYourCustomer(models.Model):
    _name = 'know.your.customer'
    _description = 'Know Your Customer'
    _order = "full_name asc"

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, default=lambda self: _('New')) 
    full_name = fields.Char(string="Full Name")
    first_name = fields.Char(string="First Name")
    other_name = fields.Char(string="Other Name")
    surname = fields.Char(string="Surname")
    gender = fields.Char(string="Gender")
    id_number = fields.Char(string="ID Number")
    id_type = fields.Char(string="ID Type")
    country_id = fields.Many2one('res.country', string='Country')
    citizenship = fields.Char(string="Citizenship")
    place_of_birth = fields.Char(string="Place Of Birth")
    date_of_birth = fields.Char(string="Date Of Birth")
    date_of_death = fields.Char(string="Date Of Death")
    id_issuance_date = fields.Char(string="ID Issuance Date")
    id_expiration_date = fields.Char(string="ID Expiration Date")
    pin = fields.Char(string="PIN")
    phone_number_1 = fields.Char(string="Phone Number 1")
    phone_number_2 = fields.Char(string="Phone Number 2")
    secondary_id_number = fields.Char(string="Secondary ID Number")
    smile_id_job = fields.Char(string="Smile Job Id")
    user_id = fields.Char(string="Searched By")
    job_id = fields.Char(string="Job Id")
    job_type = fields.Integer(string="Job Type")
    result_type = fields.Char(string="Result Type")
    result_text = fields.Char(string="Result Text")
    result_code = fields.Char(string="Result Code")
    is_final_result = fields.Char(string="Is Final Result?")
    verify_id_number = fields.Char(string="Verify ID Number")
    return_personal_info = fields.Char(string="Return Personal Info")
    error_occurred = fields.Boolean(string="Error Occurred")
    error_code = fields.Char(string="Error Code")
    error_message = fields.Char(string="Error Message")
    source = fields.Char(string="Data Source")
    signature = fields.Char(string="Signature")
    timestamp = fields.Char(string="Timestamp")
    partner_ids = fields.One2many('res.partner', 'kyc_id', string="Partners", copy=True, auto_join=True)                                      

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'know.your.customer') or _('New')
        res = super(KnowYourCustomer, self).create(vals)
        return res    

    def search_kyc_data_from_odoo_or_smile_id(self, id_number, id_type, country_code): 
        _country = self.env['res.country'].sudo().search([('code', '=', country_code)], limit=1)

        if _country:
            customer_data = self.env['know.your.customer'].search(
                [
                    ('id_number','=', id_number),
                    ('id_type','=', id_type),
                    ('country_id','=', _country.id)            
                ], limit=1
            )

            if customer_data:
                return self.convert_kyc_data_to_json(id_number, customer_data)
            else:
                # Search KYC data from Smile ID & save the results if verified
                return self.get_kyc_data_as_json(id_number, id_type, country_code)
        else:
            message = "%s is an invalid country code" % country_code
            return { "data": {}, "message": message }            
            
    def convert_kyc_data_to_json(self, search_param, data):
        message = "OK"
        customer = dict()

        if len(data) == 1:
            partner_list = []

            for p in data:
                customer['kyc_id'] = p.kyc_id
                customer['id_number'] = p.id_number
                customer['full_name'] = p.full_name
                customer['first_name'] = p.first_name
                customer['other_name'] = p.other_name                 
                customer['surname'] = p.surname
                customer['gender'] = p.gender
                customer['country'] = p.country_id.name
                customer['citizenship'] = p.citizenship   
                customer['place_of_birth'] = p.place_of_birth
                customer['date_of_birth'] = p.date_of_birth
                customer['date_of_death'] = p.date_of_death
                customer['id_issuance_date'] = p.id_issuance_date 
                customer['id_expiration_date'] = p.id_expiration_date 
                customer['pin'] = p.pin
                customer['id_type'] = p.id_type
                customer['result_type'] = p.result_type
                customer['verify_id_number'] = p.verify_id_number
                customer['result_code'] = p.result_code
                customer['result_text'] = p.result_text
                customer['return_personal_info'] = p.return_personal_info
                customer['is_final_result'] = p.is_final_result
                
                if p.partner_ids:
                    for partner in p.partner_ids:
                        partner_list.append(
                            {
                                'id': partner.id,
                                'name': partner.name
                            }
                        )
                        
                    customer['partner'] = partner_list
                else:
                    customer['partner'] = partner_list

            message = "Success"
        elif len(data) > 1:
            message = "Multiple records exist for %s.Contact `CrowPay` to resolve the issue" % search_param
        elif len(data) == 0:
            message = "Customer data not found"

        return { "data": customer, "message": message }

    def get_kyc_data_as_json(self, id_number, id_type, country_code):
        """Searches KYC data from Smile ID API and returns a JSON"""

        customer = dict()
        message = "Success"
        odoo_logged_in_user = {"id": self.env.user.id, "name": self.env.user.name}
        
        smile_identity_base_url = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_base_url')
        smile_identity_partner_id = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_partner_id')
        smile_identity_api_key = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_api_key')
        smile_identity_header = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_header')
        default_timezone = pytz.timezone(self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_timezone'))
        
        timestamp = datetime.now().isoformat()
        partner_id = smile_identity_partner_id
        api_key = smile_identity_api_key

        # Generate Smile ID Signature
        hmac_new = hmac.new(api_key.encode("utf-8"), digestmod=hashlib.sha256)
        hmac_new.update(timestamp.encode("utf-8"))
        hmac_new.update(str(partner_id).encode("utf-8"))
        hmac_new.update("sid_request".encode("utf-8"))                
        generated_signature = base64.b64encode(hmac_new.digest()).decode("utf-8")

        headers = {
            'Content-Type': smile_identity_header,
            'Accept': smile_identity_header,
            "Accept-Language": "en_US"
        }

        _country = self.env['res.country'].sudo().search([('code', '=', country_code)], limit=1)            

        body = {
            "source_sdk": "rest_api",
            "source_sdk_version": "1.0.0",
            "country": _country.name,
            "id_type": id_type,
            "id_number": id_number,
            "signature": generated_signature,
            "timestamp": timestamp,
            "partner_id": partner_id,
            "partner_params": {
                "user_id": odoo_logged_in_user['name'] + ",UID: " + str(odoo_logged_in_user['id']) + " on " + datetime.now(default_timezone).strftime("%a, %d %b %Y %-I:%M %p %Z"),
                "job_id": "ESCROW-"+ timestamp,
                "job_type": 5
            }                
        }

        my_data = json.dumps(body)

        send_request = requests.post(url=smile_identity_base_url, data=my_data, headers=headers)
        smile_identity_response = send_request.json()

        try:    
            the_id_number = smile_identity_response['IDNumber']
            verify_id_number = smile_identity_response['Actions']['Verify_ID_Number']
            result_type = smile_identity_response['ResultType']
            result_code = smile_identity_response['ResultCode']
            result_text = smile_identity_response['ResultText']
            return_personal_info = smile_identity_response['Actions']['Return_Personal_Info']
            the_country_id = _country.id if _country else False
            id_type = smile_identity_response['IDType']
            is_final_result = smile_identity_response['IsFinalResult']           

            if result_code == "1012" and verify_id_number == "Verified":
                customer_data = self.env['know.your.customer'].search(
                    [
                        ('id_number','=', id_number),
                        ('id_type','=', id_type),
                        ('country_id','=', _country.id)            
                    ], limit=1
                )

                if customer_data:
                    return self.convert_kyc_data_to_json(id_number, customer_data)
                else:
                    kyc = {
                        "smile_id_job": smile_identity_response['SmileJobID'],
                        "result_type": result_type,
                        "result_text": result_text,
                        "result_code": result_code,
                        'is_final_result': is_final_result,
                        'user_id': smile_identity_response['PartnerParams']['user_id'],
                        'job_id': smile_identity_response['PartnerParams']['job_id'],
                        'job_type': smile_identity_response['PartnerParams']['job_type'],
                        'verify_id_number': verify_id_number,
                        'return_personal_info': return_personal_info,
                        'country_id': the_country_id,
                        'id_type': id_type,
                        'id_number': the_id_number,
                        'id_expiration_date': smile_identity_response['ExpirationDate'],
                        'full_name': smile_identity_response['FullName'],
                        'phone_number_1': smile_identity_response['PhoneNumber'],
                        'phone_number_2': smile_identity_response['PhoneNumber2'],
                        'secondary_id_number': smile_identity_response['Secondary_ID_Number'],
                        'source': smile_identity_response['Source'],
                        'signature': smile_identity_response['signature'],
                        'timestamp': smile_identity_response['timestamp'],
                        'gender': smile_identity_response['FullData']['Gender'],
                        'first_name': smile_identity_response['FullData']['First_Name'],
                        'other_name': smile_identity_response['FullData']['Other_Name'],
                        'surname': smile_identity_response['FullData']['Surname'],
                        'place_of_birth': smile_identity_response['FullData']['Place_of_Birth'],
                        'date_of_birth': smile_identity_response['DOB'],
                        'date_of_death': smile_identity_response['FullData']['Date_of_Death'],
                        'citizenship': smile_identity_response['FullData']['Citizenship'],
                        'id_issuance_date': smile_identity_response['FullData']['Date_of_Issue'],
                        'pin': smile_identity_response['FullData']['Pin'],
                        'error_occurred': smile_identity_response['FullData']['ErrorOcurred'],
                        'error_code': smile_identity_response['FullData']['ErrorCode'],
                        'error_message': smile_identity_response['FullData']['ErrorMessage'],
                    }

                    # Save the record
                    create_kyc = self.env['know.your.customer'].create(kyc)

                    if create_kyc:
                        customer['kyc_id'] = create_kyc.id
                        customer['id_number'] = the_id_number
                        customer['full_name'] = smile_identity_response['FullName']
                        customer['first_name'] = smile_identity_response['FullData']['First_Name']
                        customer['other_name'] = smile_identity_response['FullData']['Other_Name']                 
                        customer['surname'] = smile_identity_response['FullData']['Surname']
                        customer['gender'] = smile_identity_response['FullData']['Gender']
                        customer['country'] = _country.name
                        customer['citizenship'] = smile_identity_response['FullData']['Citizenship']   
                        customer['place_of_birth'] = smile_identity_response['FullData']['Place_of_Birth']
                        customer['date_of_birth'] = smile_identity_response['FullData']['Date_of_Birth']
                        customer['date_of_death'] = smile_identity_response['FullData']['Date_of_Death']
                        customer['id_issuance_date'] = smile_identity_response['FullData']['Date_of_Issue']
                        customer['id_expiration_date'] = smile_identity_response['ExpirationDate']
                        customer['pin'] = smile_identity_response['FullData']['Pin']
                        customer['id_type'] = id_type
                        customer['result_type'] = result_type
                        customer['verify_id_number'] = verify_id_number
                        customer['result_code'] = result_code
                        customer['result_text'] = result_text
                        customer['return_personal_info'] = return_personal_info
                        customer['is_final_result'] = is_final_result
                    else:
                        message = "Failed to save the customers' details"

                    return { "data": customer, "message": message }
            else:
                return { 
                    "data": {
                        "id_number": the_id_number,
                        "id_type": id_type,
                        "country": _country.name,
                        "result_type": result_type,
                        "verify_id_number": verify_id_number, 
                        "result_code": result_code,
                        "result_text": result_text,
                        "return_personal_info": return_personal_info,
                        "is_final_result": is_final_result,
                    }, 
                    "message": "Success"
                }
        except Exception:
            return smile_identity_response

    def get_kyc_data_as_tuple(self, id_number, id_type, country_code):
        """Searches KYC data from Smile ID API and returns a tuple.
        This method was designed for the KYC wizard"""
        
        smile_identity_base_url = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_base_url')
        smile_identity_partner_id = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_partner_id')
        smile_identity_api_key = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_api_key')
        smile_identity_header = self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_header')
        default_timezone = pytz.timezone(self.env['ir.config_parameter'].sudo().get_param('smile_identity.smile_identity_timezone'))
        
        timestamp = datetime.now().isoformat()
        partner_id = smile_identity_partner_id
        api_key = smile_identity_api_key
        odoo_logged_in_user = {"id": self.env.user.id, "name": self.env.user.name}

        # Generate Smile ID Signature
        hmac_new = hmac.new(api_key.encode("utf-8"), digestmod=hashlib.sha256)
        hmac_new.update(timestamp.encode("utf-8"))
        hmac_new.update(str(partner_id).encode("utf-8"))
        hmac_new.update("sid_request".encode("utf-8"))                
        generated_signature = base64.b64encode(hmac_new.digest()).decode("utf-8")

        headers = {
            'Content-Type': smile_identity_header,
            'Accept': smile_identity_header,
            "Accept-Language": "en_US"
        }

        try:
            _country = self.env['res.country'].sudo().search([('code', '=', country_code)], limit=1)

            body = {
                "source_sdk": "rest_api",
                "source_sdk_version": "1.0.0",
                "country": _country.code,
                "id_type": id_type,
                "id_number": id_number,
                "signature": generated_signature,
                "timestamp": timestamp,
                "partner_id": partner_id,
                "partner_params": {
                    "user_id": odoo_logged_in_user['name'] + ",UID: " + str(odoo_logged_in_user['id']) + " on " + datetime.now(default_timezone).strftime("%a, %d %b %Y %-I:%M %p %Z"),
                    "job_id": "REGENFLI-"+ timestamp,
                    "job_type": 5
                }                
            }

            my_data = json.dumps(body)

            send_request = requests.post(url=smile_identity_base_url, data=my_data, headers=headers)
            smile_identity_response = send_request.json()

            the_id_number = smile_identity_response['IDNumber']
            verify_id_number = smile_identity_response['Actions']['Verify_ID_Number']
            result_type = smile_identity_response['ResultType']
            result_code = smile_identity_response['ResultCode']
            result_text = smile_identity_response['ResultText']
            return_personal_info = smile_identity_response['Actions']['Return_Personal_Info']
            the_country_id = _country.id if _country else False
            id_type = smile_identity_response['IDType']
            is_final_result = smile_identity_response['IsFinalResult']           

            if result_code == "1012" and verify_id_number == "Verified":
                customer_data = self.env['know.your.customer'].search(
                    [
                        ('id_number','=', id_number),
                        ('id_type','=', id_type),
                        ('country_id','=', _country.name)            
                    ]
                )

                if customer_data:
                    return customer_data
                else:
                    kyc = {
                        "smile_id_job": smile_identity_response['SmileJobID'],
                        "result_type": result_type,
                        "result_text": result_text,
                        "result_code": result_code,
                        'is_final_result': is_final_result,
                        'user_id': smile_identity_response['PartnerParams']['user_id'],
                        'job_id': smile_identity_response['PartnerParams']['job_id'],
                        'job_type': smile_identity_response['PartnerParams']['job_type'],
                        'verify_id_number': verify_id_number,
                        'return_personal_info': return_personal_info,
                        'country_id': the_country_id,
                        'id_type': id_type,
                        'id_number': the_id_number,
                        'id_expiration_date': smile_identity_response['ExpirationDate'],
                        'full_name': smile_identity_response['FullName'],
                        'phone_number_1': smile_identity_response['PhoneNumber'],
                        'phone_number_2': smile_identity_response['PhoneNumber2'],
                        'secondary_id_number': smile_identity_response['Secondary_ID_Number'],
                        'source': smile_identity_response['Source'],
                        'signature': smile_identity_response['signature'],
                        'timestamp': smile_identity_response['timestamp'],
                        'gender': smile_identity_response['FullData']['Gender'],
                        'first_name': smile_identity_response['FullData']['First_Name'],
                        'other_name': smile_identity_response['FullData']['Other_Name'],
                        'surname': smile_identity_response['FullData']['Surname'],
                        'place_of_birth': smile_identity_response['FullData']['Place_of_Birth'],
                        'date_of_birth': smile_identity_response['DOB'],
                        'date_of_death': smile_identity_response['FullData']['Date_of_Death'],
                        'citizenship': smile_identity_response['FullData']['Citizenship'],
                        'id_issuance_date': smile_identity_response['FullData']['Date_of_Issue'],
                        'pin': smile_identity_response['FullData']['Pin'],
                        'error_occurred': smile_identity_response['FullData']['ErrorOcurred'],
                        'error_code': smile_identity_response['FullData']['ErrorCode'],
                        'error_message': smile_identity_response['FullData']['ErrorMessage'],
                    }

                    # Save the record
                    create_kyc = self.env['know.your.customer'].create(kyc)

                    if create_kyc:
                        customer_data = self.env['know.your.customer'].search([('id','=', create_kyc.id)])

                    return customer_data                                                
        except Exception:
            raise ValidationError(smile_identity_response['error'])

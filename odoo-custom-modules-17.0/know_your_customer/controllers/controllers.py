from odoo import http
from odoo.http import request, Response
import json

class KnowYourCustomer(http.Controller):
    @http.route('/kyc', methods=['GET'], type='http', auth='public')
    def get_customer_details(self, **kw):
        id_number = request.params.get('id_number')
        id_type = request.params.get('id_type')
        country_code = request.params.get('country_code')
        headers = {'Content-Type': 'application/json'}    

        if id_number and id_type and country_code:
            kyc = request.env['know.your.customer'].sudo().search_kyc_data_from_odoo_or_smile_id(id_number, id_type, country_code)
            try:
                return Response(json.dumps({"data": kyc['data'], "message": kyc['message']}), headers=headers)
            except Exception:             
                return Response(json.dumps({"data": {}, "message3": kyc['error']}), headers=headers)                       
        else:
            error = "ID Number, ID Type and Country Code are required"
            return Response(json.dumps({"data": {}, "message": error}), headers=headers)
            
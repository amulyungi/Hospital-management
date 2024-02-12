# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class Services(http.Controller):
    @http.route('/api/v1/service/category', methods=['GET'], auth='user', type='http')
    def get_service_categories(self, **kw):
        """Get the Service Categories"""
        
        headers = {'Content-Type': 'application/json'}        

        try:
            service_categories = request.env['service.category'].sudo().get_service_categories()
            
            # A validation that checks whether a dictionary has been returned and if it contains any data
            if isinstance(service_categories, dict) and len(service_categories['data']) > 0:
                return Response(
                    json.dumps(                        
                        {
                            "data": service_categories['data'],
                            "message": "Success"
                        }
                    ), headers=headers, status=200
                )
            else:
                return Response(
                    json.dumps(
                        {
                            "data": service_categories['data'],                            
                            "message": "Not Found"
                        }
                    ), headers=headers, status=404)
        except Exception as e:
            return Response(
                json.dumps(
                    {
                        "message": e
                    }, 
                    default=str
                ), headers=headers, status=500)
        
    @http.route('/api/v1/service/category/services', methods=['GET'], auth='user', type='http')
    def get_services(self, **kw):
        """Get the Services Offered"""
        
        category_id = int(request.params.get('category_id'))
        headers = {'Content-Type': 'application/json'}        

        try:
            services_offered = request.env['services'].sudo().get_services_offered(category_id)
            
            # A validation that checks whether a dictionary has been returned and if it contains any data
            if isinstance(services_offered, dict) and len(services_offered['data']) > 0:
                return Response(
                    json.dumps(                        
                        {
                            "data": services_offered['data'],
                            "message": "Success"
                        }
                    ), headers=headers, status=200
                )
            else:
                return Response(
                    json.dumps(
                        {
                            "data": services_offered['data'],                            
                            "message": "Not Found"
                        }
                    ), headers=headers, status=404)
        except Exception as e:
            return Response(
                json.dumps(
                    {
                        "message": e
                    }, 
                    default=str
                ), headers=headers, status=500)        

# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
from odoo.tools import date_utils

import json
import logging

_logger = logging.getLogger(__name__)


class HospitalManagement(http.Controller):
    @http.route('/api/v1/appointment', methods=['POST'], auth='user', type='json')
    def create_appointment(self, **kw):
        """Create an appointment"""
                          
        response_data = dict()
        status_code = 200
        
        try:
            data = json.loads(request.httprequest.data)
            headers = [
                ('Content-Type', 'application/json')
            ]                        

            appointment = request.env['medical.appointment'].create_appointment(data)
            
            if appointment:
                response_data["appointment_id"] = appointment.id
                response_data["message"] = "Appointment created"
            else:
                status_code = 204
                response_data["message"] = "Failed to create the appointment"
                
            return request.make_json_response(response_data, headers=headers, status=status_code)
            
        except Exception as e:
            status_code = 500
            response_data["message"] = str(e)            
            _logger.error("Error: Failed to create the appointment\n"  + str(e))
            
            return request.make_json_response(response_data, headers=headers, status=status_code)
            
        
        
    @http.route('/api/v1/appointment', methods=['GET'], auth='user', type='http')
    def get_appointment(self, **kw):
        """Get the appointment details"""
        
        response_data = dict()
        query_param = []
        status_code = 200        
        headers = [
            ('Content-Type', 'application/json')
        ]

        try:
            appointment_id = request.params.get('id')
            patient_id = request.params.get('patient_id')
            doctor_id = request.params.get('doctor_id')
        
            if appointment_id:
                query_param.append(('id', '=', int(appointment_id)))
            elif doctor_id:
                query_param.append(('doctor_id', '=', int(doctor_id)))
            elif patient_id:
                query_param.append(('patient_id', '=', int(patient_id)))
            else:
                status_code = 400
                response_data["message"] = "No search parameters were provided"
 
            appointment = request.env['medical.appointment'].get_appointment(query_param)
            
            if appointment:
                response_data = appointment
                response_data["message"] = "Success"          
            else:
                status_code = 404
                response_data["message"] = "Appointment not found"
                              
            return request.make_json_response(response_data, headers=headers, status=status_code)            
                
        except Exception as e:
            status_code = 500
            response_data["message"] = str(e)           
            _logger.error("Error: Failed to get the appointment\n"  + str(e))
            
            return request.make_json_response(response_data, headers=headers, status=status_code)                   

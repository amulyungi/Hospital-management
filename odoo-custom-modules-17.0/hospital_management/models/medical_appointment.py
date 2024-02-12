from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request, Response
from datetime import datetime, timedelta


import logging
import pytz

_logger = logging.getLogger(__name__)

class CustomMedicalAppointment(models.Model):
    _inherit = "medical.appointment"

    
    def create_appointment(self, data):
        """Create an appointment"""
        
        # logged_in_user = self.env.user.partner_id.id
        response_data = dict()

        try:
            # admin = self.env["res.users"].sudo().search([("id","=", 2)])
            
            appointment_details = {
                "patient_id": int(data.get("patient_id")),
                "doctor_id": int(data.get("doctor_id")),
                "institution_partner_id": int(data.get("medical_center")), 
                "appointment_end": data.get("appointment_end_date"),
                "urgency_level": data.get("urgency_level") if data.get("urgency_level") else "a",
                "consultations_id": int(data.get("consultation_service_id")),
                "appointment_validity_date": datetime.now(),
                "no_invoice": True if data.get("invoice_the_patient") == True else False,
                "invoice_to_insurer": True if data.get("invoice_the_insurer") == True else False,
                "patient_status": data.get("patient_status") if data.get("patient_status") else "outpatient"                        
            }
            
            appointment = self.env["medical.appointment"].create(appointment_details)
            return appointment
        except Exception as e:
            _logger.error("Error: Failed to create the appointment\n"  + str(e))
            response_data["message"] = str(e)
            return request.make_json_response(response_data, status=500)            
            # return e
        
    def get_appointment(self, query_param):
        """Get the appointment details"""        
        
        # now_utc = datetime.now(pytz.UTC)
        # now_user = now_utc.astimezone(pytz.timezone(self.env.user.tz or 'UTC'))
        # today_user = now_user.date()        
        
        try:
            response_data = dict()        
            appointment = self.env["medical.appointment"].search(query_param)

            if appointment:
                response_data["appointment_id"] = appointment.id
                response_data["appointment_name"] = appointment.name    
                response_data["patient_id"] = appointment.patient_id.id
                response_data["patient_name"] = appointment.patient_id.name                
                response_data["doctor_id"] = appointment.doctor_id.id
                response_data["doctor_name"] = appointment.doctor_id.partner_id.name
                response_data["medical_center_id"] = appointment.institution_partner_id.id
                response_data["medical_center_name"] = appointment.institution_partner_id.name
                # start_date = (appointment.appointment_date).now(pytz.UTC)    
                # my_time = start_date.astimezone(pytz.timezone(self.env.user.tz or 'UTC'))                            
                response_data["appointment_start_date"] = appointment.appointment_date                   
                response_data["appointment_end_date"] = appointment.appointment_end   
                response_data["urgency_level"] = appointment.urgency_level
                response_data["appointment_validity_date"] = appointment.appointment_validity_date
                response_data["patient_status"] = appointment.patient_status #This is labeled as `Invoiced` on the UI
                response_data["invoice_the_patient"] = appointment.no_invoice
                response_data["invoice_the_insurer"] = appointment.invoice_to_insurer              
                response_data["consultation_service_id"] = appointment.consultations_id.id
                response_data["consultation_service_name"] = appointment.consultations_id.name                

            return response_data
        except Exception as e:
            _logger.error("Error: Failed to get the appointment\n"  + str(e))            
            return e
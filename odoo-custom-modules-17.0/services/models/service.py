from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class Services(models.Model):
    _name = 'services'
    _description = 'Service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name desc"

    name = fields.Char(string="Service Name", tracking=True)
    description = fields.Text(string="Description", tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("publish", "Publish"),
            ("unpublish", "Unpublish")
        ], string='Status', default='draft', tracking=True
    )   
    service_category_id = fields.Many2one('service.category', string='Service Category')
    
    def publish_service(self):
        self.state = "publish"
        
    def unpublish_service(self):
        self.state = "unpublish"
        
    def get_services_offered(self, category_id):
        """Get all published services via service category id"""        
        
        try:
            service_list = []       
            services = self.env["services"].search([("state", "=", "publish"), ("service_category_id", "=", category_id)])

            if services:
                for service in services:
                    service_offered = dict()
                    service_offered['id'] = service.id
                    service_offered['name'] = service.name
                    service_offered['description'] = service.description
                    
                    service_list.append(service_offered)

            return { "data": service_list }  
        except Exception as e:
            return e            
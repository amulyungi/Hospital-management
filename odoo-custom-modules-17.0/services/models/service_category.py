from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class ServiceCategory(models.Model):
    _name = 'service.category'
    _description = 'Service Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name desc"

    name = fields.Char(string='Service Category', tracking=True)
    description = fields.Text(string="Description", tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("publish", "Publish"),
            ("unpublish", "Unpublish")
        ], string='Status', default='draft', tracking=True
    )
    service_ids = fields.One2many('services', 'service_category_id',
        string="Services", copy=True, auto_join=True)
    service_count = fields.Integer(string="No. Of Services", 
        compute="_compute_service_count")    
    
    def _compute_service_count(self):
        for rec in self:
            service_counter = self.env['services'].search_count([('service_category_id', '=', rec.id)])
            rec.service_count = service_counter
                
    def action_view_services(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": "Services",
            "res_model": "services",
            "domain": [('id', 'in', self.service_ids.ids)],
            "view_mode": "tree",
            "context": {'create': False, 'default_service_category_id': self.id}
        }
        
        return action
    
    def publish_service_category(self):
        self.state = "publish"
        
    def unpublish_service_category(self):
        self.state = "unpublish"        
    
    def get_service_categories(self):
        """Get all published Service Categories"""        
        
        try:
            service_category_list = []       
            service_categories = self.env["service.category"].search([("state", "=", "publish")])

            if service_categories:
                for category in service_categories:
                    service_category = dict()
                    service_category['id'] = category.id
                    service_category['name'] = category.name
                    service_category['description'] = category.description
                    
                    service_category_list.append(service_category)

            return { "data": service_category_list }  
        except Exception as e:
            return e
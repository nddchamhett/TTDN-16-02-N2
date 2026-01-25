# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_enabled = fields.Boolean(
        string='Bật AI',
        config_parameter='quan_ly_du_an.ai_enabled',
    )
    ai_api_key = fields.Char(
        string='API Key',
        config_parameter='quan_ly_du_an.ai_api_key',
    )
    ai_base_url = fields.Char(
        string='Base URL',
        config_parameter='quan_ly_du_an.ai_base_url',
        default='https://generativelanguage.googleapis.com/v1beta',
    )
    ai_model = fields.Char(
        string='Model',
        config_parameter='quan_ly_du_an.ai_model',
        default='gemini-2.5-flash',
    )
    ai_timeout = fields.Integer(
        string='Timeout (giây)',
        config_parameter='quan_ly_du_an.ai_timeout',
        default=30,
    )

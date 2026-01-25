from odoo import http
from odoo.http import request


class QuanLyDuAnController(http.Controller):
    """Ví dụ controller đơn giản cho module quản lý dự án."""

    @http.route('/quan_ly_du_an/du_an', auth='user', type='json')
    def list_du_an(self, **kwargs):
        """Trả về danh sách dự án ở dạng JSON để minh họa controller của module."""
        projects = request.env['du_an'].sudo().search([])
        return [
            {
                'id': p.id,
                'ten_du_an': p.ten_du_an,
                'tien_do_du_an': p.tien_do_du_an,
                'phan_tram_du_an': p.phan_tram_du_an,
            }
            for p in projects
        ]

{
  "cells": [],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}
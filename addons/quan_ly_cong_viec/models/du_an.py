from odoo import models, fields, api


class DuAn(models.Model):
    _inherit = 'du_an'

    cong_viec_ids = fields.One2many(
        'cong_viec',
        'du_an_id',
        string='Công Việc',
    )
    nhat_ky_cong_viec_ids = fields.One2many(
        'nhat_ky_cong_viec',
        'du_an_id',
        string='Nhật Ký Công Việc',
    )
    danh_gia_nhan_vien_ids = fields.One2many(
        'danh_gia_nhan_vien',
        'du_an_id',
        string='Đánh Giá Nhân Viên',
    )

    tong_so_cong_viec = fields.Integer(
        string='Tổng Số Công Việc',
        compute='_compute_cong_viec_stats',
        store=True,
    )
    so_cong_viec_hoan_thanh = fields.Integer(
        string='Số Công Việc Hoàn Thành',
        compute='_compute_cong_viec_stats',
        store=True,
    )

    @api.depends('cong_viec_ids', 'cong_viec_ids.phan_tram_cong_viec')
    def _compute_cong_viec_stats(self):
        for record in self:
            cong_viec_ids = record.cong_viec_ids
            record.tong_so_cong_viec = len(cong_viec_ids)
            record.so_cong_viec_hoan_thanh = len(
                cong_viec_ids.filtered(lambda cv: (cv.phan_tram_cong_viec or 0.0) >= 100.0)
            )

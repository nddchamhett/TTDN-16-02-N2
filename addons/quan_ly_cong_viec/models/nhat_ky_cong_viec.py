from odoo import api, models, fields
from odoo.exceptions import ValidationError

class NhatKyCongViec(models.Model):
    _name = 'nhat_ky_cong_viec'
    _description = 'Nhật Ký Công Việc'

    cong_viec_id = fields.Many2one('cong_viec', string='Công Việc', ondelete='cascade')
    # Lưu trực tiếp dự án, làm inverse cho One2many nhat_ky_cong_viec_ids trên model du_an
    du_an_id = fields.Many2one('du_an', string='Dự Án', ondelete='cascade')

    nhan_vien_ids = fields.Many2many('nhan_vien', string='Người Thực Hiện', ondelete='cascade')

    ngay_thuc_hien = fields.Datetime(string='Ngày Thực Hiện', default=fields.Datetime.now)

    giai_doan_id = fields.Many2one('giai_doan_cong_viec', string="Giai Đoạn", related='cong_viec_id.giai_doan_id', store=True)

    muc_do = fields.Float(
        string='Mức Độ Hoàn Thành (%)', 
        digits=(6, 2), 
        default=0.0
    )

    trang_thai = fields.Selection([
        ('chua_hoan_thanh', 'Chưa Hoàn Thành'),
        ('hoan_thanh', 'Hoàn Thành'),
    ], string='Trạng Thái', compute='_compute_trang_thai', store=True, default='chua_hoan_thanh')
    
    @api.onchange('cong_viec_id')
    def _onchange_cong_viec_id(self):
        """Khi chọn công việc, tự động gán nhân viên và dự án tương ứng."""
        if self.cong_viec_id:
            self.nhan_vien_ids = [(6, 0, self.cong_viec_id.nhan_vien_ids.ids)]
            self.du_an_id = self.cong_viec_id.du_an_id
        else:
            self.nhan_vien_ids = [(6, 0, [])]
            self.du_an_id = False

    @api.depends('cong_viec_id', 'cong_viec_id.phan_tram_cong_viec')
    def _compute_trang_thai(self):
        """Tự động cập nhật trạng thái nhật ký dựa trên tổng tiến độ công việc
        Tất cả nhật ký của cùng một công việc sẽ có cùng trạng thái:
        - Nếu tổng tiến độ công việc >= 100% → Tất cả nhật ký = "Hoàn Thành"
        - Nếu tổng tiến độ công việc < 100% → Tất cả nhật ký = "Chưa Hoàn Thành"
        """
        for record in self:
            if record.cong_viec_id and record.cong_viec_id.phan_tram_cong_viec >= 100.0:
                record.trang_thai = 'hoan_thanh'
            else:
                record.trang_thai = 'chua_hoan_thanh'

    @api.constrains('muc_do')
    def _check_muc_do(self):
        """ Kiểm tra mức độ hoàn thành phải từ 0 đến 100 """
        for record in self:
            if not (0 <= record.muc_do <= 100):
                raise ValidationError("Mức Độ Hoàn Thành phải nằm trong khoảng từ 0 đến 100.")

    @api.model
    def create(self, vals):
        record = super(NhatKyCongViec, self).create(vals)
        # Cập nhật tiến độ công việc (tổng các mức độ)
        # Trạng thái nhật ký sẽ tự động được tính toán vì là computed field
        record.cong_viec_id._compute_phan_tram_cong_viec()
        # Cập nhật tiến độ dự án
        record.cong_viec_id.du_an_id._compute_phan_tram_du_an()
        return record

    def write(self, vals):
        res = super(NhatKyCongViec, self).write(vals)
        for record in self:
            # Cập nhật tiến độ công việc (tổng các mức độ)
            # Trạng thái nhật ký sẽ tự động được tính toán vì là computed field
            record.cong_viec_id._compute_phan_tram_cong_viec()
            # Cập nhật tiến độ dự án
            record.cong_viec_id.du_an_id._compute_phan_tram_du_an()
        return res

    def unlink(self):
        cong_viec_ids = self.mapped('cong_viec_id')
        res = super(NhatKyCongViec, self).unlink()
        for cong_viec in cong_viec_ids:
            # Cập nhật tiến độ công việc sau khi xóa nhật ký
            # Trạng thái nhật ký sẽ tự động được tính toán vì là computed field
            cong_viec._compute_phan_tram_cong_viec()
            # Cập nhật tiến độ dự án
            cong_viec.du_an_id._compute_phan_tram_du_an()
        return res


    phan_tram_cong_viec = fields.Float(string="Tiến Độ Công Việc", compute="_compute_phan_tram_cong_viec", store=True)

    @api.depends('cong_viec_id', 'cong_viec_id.phan_tram_cong_viec')
    def _compute_phan_tram_cong_viec(self):
        for record in self:
            record.phan_tram_cong_viec = record.cong_viec_id.phan_tram_cong_viec if record.cong_viec_id else 0.0

    @api.constrains('nhan_vien_ids')
    def _check_nhan_vien_nhat_ky(self):
        for record in self:
            if record.du_an_id:
                nhan_vien_du_an_ids = record.du_an_id.nhan_vien_ids.ids
                for nhan_vien in record.nhan_vien_ids:
                    if nhan_vien.id not in nhan_vien_du_an_ids:
                        raise ValidationError(f"Nhân viên {nhan_vien.display_name} không thuộc dự án này.")

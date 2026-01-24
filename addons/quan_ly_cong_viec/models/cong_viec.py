from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class CongViec(models.Model):
    _name = 'cong_viec'
    _description = 'Công Việc Dự Án'
    _rec_name = 'ten_cong_viec'

    ten_cong_viec = fields.Char(string='Tên Công Việc' )
    mo_ta = fields.Text(string='Mô Tả')
    du_an_id = fields.Many2one('du_an', string='Dự Án', required=True, ondelete='cascade')

    nhan_vien_ids = fields.Many2many('nhan_vien', 'cong_viec_nhan_vien_rel', 'cong_viec_id', 'nhan_vien_id', string='Nhân Viên Tham Gia')

    han_chot = fields.Datetime(string='Hạn Chót')
    giai_doan_id = fields.Many2one('giai_doan_cong_viec', string='Giai Đoạn')

    nhat_ky_cong_viec_ids = fields.One2many('nhat_ky_cong_viec', 'cong_viec_id', string='Nhật Ký Công Việc')

    thoi_gian_con_lai = fields.Char(string="Thời Gian Còn Lại", compute="_compute_thoi_gian_con_lai", store=True)
    
    danh_gia_nhan_vien_ids = fields.One2many('danh_gia_nhan_vien', 'cong_viec_id', string='Đánh Giá Nhân Viên')
    
    tai_nguyen_cong_viec_ids = fields.One2many('tai_nguyen_cong_viec', 'cong_viec_id', string='Tài Nguyên Sử Dụng')
    
    nhan_vien_display = fields.Char(string="Nhân Viên Tham Gia (Tên + Mã Định Danh)", compute="_compute_nhan_vien_display")

    phan_tram_cong_viec = fields.Float(
        string="Phần Trăm Hoàn Thành", 
        compute="_compute_phan_tram_cong_viec", 
        store=True
    )
    
    trang_thai_cong_viec = fields.Selection([
        ('chua_hoan_thanh', 'Chưa Hoàn Thành'),
        ('hoan_thanh', 'Hoàn Thành'),
    ], string='Trạng Thái Công Việc', compute='_compute_trang_thai_cong_viec', store=True, default='chua_hoan_thanh')

    @api.depends('nhat_ky_cong_viec_ids.muc_do')
    def _compute_phan_tram_cong_viec(self):
        """Tính tiến độ công việc bằng tổng các mức độ trong nhật ký
        Ví dụ: Nhật ký 1: 10%, Nhật ký 2: 10% → Tiến độ công việc = 20%
        """
        for record in self:
            if record.nhat_ky_cong_viec_ids:
                # Tính tổng các mức độ hoàn thành trong nhật ký
                total_progress = sum(record.nhat_ky_cong_viec_ids.mapped('muc_do'))
                # Giới hạn tối đa 100%
                record.phan_tram_cong_viec = min(total_progress, 100.0)
            else:
                record.phan_tram_cong_viec = 0.0
            # Cập nhật tiến độ dự án khi phần trăm công việc thay đổi
            if record.du_an_id:
                record.du_an_id._compute_phan_tram_du_an()
    
    @api.depends('phan_tram_cong_viec')
    def _compute_trang_thai_cong_viec(self):
        """Tự động cập nhật trạng thái công việc dựa trên tiến độ
        Nếu tiến độ = 100% → Hoàn Thành, ngược lại → Chưa Hoàn Thành
        """
        for record in self:
            if record.phan_tram_cong_viec >= 100.0:
                record.trang_thai_cong_viec = 'hoan_thanh'
            else:
                record.trang_thai_cong_viec = 'chua_hoan_thanh'

    
    @api.depends('nhan_vien_ids')
    def _compute_nhan_vien_display(self):
        for record in self:
            record.nhan_vien_display = ', '.join(record.nhan_vien_ids.mapped('display_name'))

    @api.depends('han_chot')
    def _compute_thoi_gian_con_lai(self):
        for record in self:
            if record.han_chot:
                now = datetime.now()
                delta = record.han_chot - now
                if delta.total_seconds() > 0:
                    days = delta.days
                    hours = delta.seconds // 3600
                    record.thoi_gian_con_lai = f"{days} ngày, {hours} giờ"
                else:
                    record.thoi_gian_con_lai = "Hết hạn"
            else:
                record.thoi_gian_con_lai = "Chưa có hạn chót"

    
    @api.onchange('du_an_id')
    def _onchange_du_an_id(self):
        if self.du_an_id:
            self.nhan_vien_ids = [(6, 0, self.du_an_id.nhan_vien_ids.ids)]

            
    @api.constrains('du_an_id')
    def _check_du_an_tien_do(self):
        for record in self:
            if record.du_an_id and record.du_an_id.tien_do_du_an == 'hoan_thanh':
                raise ValidationError("Không thể thêm công việc vào dự án đã hoàn thành.")
    
    

    @api.constrains('nhan_vien_ids')
    def _check_nhan_vien_trong_du_an(self):
        for record in self:
            if record.du_an_id:
                nhan_vien_du_an_ids = record.du_an_id.nhan_vien_ids.ids
                for nhan_vien in record.nhan_vien_ids:
                    if nhan_vien.id not in nhan_vien_du_an_ids:
                        raise ValidationError(f"Nhân viên {nhan_vien.display_name} không thuộc dự án này.")

    @api.model
    def create(self, vals):
        """Tạo công việc và cập nhật tiến độ dự án"""
        record = super(CongViec, self).create(vals)
        # Cập nhật tiến độ dự án khi tạo công việc mới
        if record.du_an_id:
            record.du_an_id._compute_phan_tram_du_an()
        return record

    def unlink(self):
        """Xóa công việc và cập nhật tiến độ dự án"""
        du_an_ids = self.mapped('du_an_id')
        result = super(CongViec, self).unlink()
        # Cập nhật tiến độ dự án sau khi xóa công việc
        for du_an in du_an_ids:
            if du_an:
                du_an._compute_phan_tram_du_an()
        return result

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TaiNguyenCongViec(models.Model):
    _name = 'tai_nguyen_cong_viec'
    _description = 'Tài Nguyên Sử Dụng Trong Công Việc'
    _rec_name = 'ten_tai_nguyen_display'

    cong_viec_id = fields.Many2one('cong_viec', string='Công Việc', required=True, ondelete='cascade')
    tai_nguyen_id = fields.Many2one('tai_nguyen', string='Tài Nguyên', required=True, ondelete='cascade')
    so_luong_su_dung = fields.Integer(string='Số Lượng Sử Dụng', required=True, default=1)
    
    # Computed field để hiển thị tên tài nguyên
    ten_tai_nguyen_display = fields.Char(string='Tên Tài Nguyên', compute='_compute_ten_tai_nguyen_display', store=True)
    
    @api.depends('tai_nguyen_id')
    def _compute_ten_tai_nguyen_display(self):
        for record in self:
            if record.tai_nguyen_id:
                record.ten_tai_nguyen_display = record.tai_nguyen_id.ten_tai_nguyen
            else:
                record.ten_tai_nguyen_display = ''
    
    @api.onchange('cong_viec_id')
    def _onchange_cong_viec_id(self):
        """Khi thay đổi công việc, xóa tài nguyên nếu không thuộc dự án mới"""
        if self.cong_viec_id and self.tai_nguyen_id:
            if self.tai_nguyen_id.du_an_id != self.cong_viec_id.du_an_id:
                self.tai_nguyen_id = False

    @api.constrains('tai_nguyen_id', 'so_luong_su_dung', 'cong_viec_id')
    def _check_so_luong_tai_nguyen(self):
        """Kiểm tra tổng số lượng tài nguyên sử dụng không vượt quá số lượng tài nguyên trong dự án"""
        for record in self:
            if not record.cong_viec_id or not record.tai_nguyen_id:
                continue
                
            # Lấy dự án từ công việc
            du_an = record.cong_viec_id.du_an_id
            if not du_an:
                continue
            
            # Lấy tài nguyên trong dự án
            tai_nguyen_du_an = record.tai_nguyen_id
            if tai_nguyen_du_an.du_an_id != du_an:
                raise ValidationError(f"Tài nguyên '{tai_nguyen_du_an.ten_tai_nguyen}' không thuộc dự án '{du_an.ten_du_an}'.")
            
            # Kiểm tra số lượng sử dụng trong công việc hiện tại phải > 0
            if record.so_luong_su_dung <= 0:
                raise ValidationError("Số lượng sử dụng phải lớn hơn 0.")
            
            # Tính tổng số lượng đã sử dụng trong tất cả công việc của dự án
            # Tìm tất cả các record sử dụng cùng tài nguyên trong cùng dự án
            all_tai_nguyen_cong_viec = self.env['tai_nguyen_cong_viec'].search([
                ('tai_nguyen_id', '=', record.tai_nguyen_id.id),
                ('cong_viec_id.du_an_id', '=', du_an.id)
            ])
            
            tong_so_luong_su_dung = 0
            for tn_cv in all_tai_nguyen_cong_viec:
                # Nếu đang cập nhật record hiện tại, sử dụng giá trị mới
                if tn_cv.id == record.id:
                    tong_so_luong_su_dung += record.so_luong_su_dung
                else:
                    tong_so_luong_su_dung += tn_cv.so_luong_su_dung
            
            # Kiểm tra tổng số lượng không vượt quá số lượng tài nguyên
            if tong_so_luong_su_dung > tai_nguyen_du_an.so_luong:
                raise ValidationError(
                    f"Tổng số lượng sử dụng tài nguyên '{tai_nguyen_du_an.ten_tai_nguyen}' "
                    f"({tong_so_luong_su_dung}) vượt quá số lượng có sẵn trong dự án ({tai_nguyen_du_an.so_luong})."
                )


from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError


class DuAn(models.Model):
    _name = 'du_an'
    _description = 'Dự Án'
    _rec_name = 'ten_du_an'

    ten_du_an = fields.Char(string='Tên Dự Án', required=True)
    mo_ta = fields.Text(string='Mô Tả')

    nguoi_phu_trach_id = fields.Many2one('nhan_vien', string='Người Phụ Trách', ondelete='set null')

    nhan_vien_ids = fields.Many2many('nhan_vien', 'du_an_nhan_vien_rel', 'du_an_id', 'nhan_vien_id', string='Nhân Viên Tham Gia')

    # Các quan hệ One2many tới model thuộc module quan_ly_cong_viec
    # sẽ được định nghĩa bên module đó để tránh phụ thuộc ngược.
    tai_nguyen_ids = fields.One2many('tai_nguyen', 'du_an_id', string='Danh Sách Tài Nguyên')
    # cong_viec_ids = fields.One2many('cong_viec', 'du_an_id', string='Công Việc')
    # danh_gia_nhan_vien_ids = fields.One2many('danh_gia_nhan_vien', 'du_an_id', string='Đánh Giá Nhân Viên')
    # nhat_ky_cong_viec_ids = fields.One2many('nhat_ky_cong_viec', 'du_an_id', string='Nhật Ký Công Việc')

    dashboard_id = fields.Many2one('dashboard', string="Dashboard")
    
    # Thêm các field ngày tháng để tự động cập nhật trạng thái
    ngay_bat_dau = fields.Date(string='Ngày Bắt Đầu', required=True)
    ngay_ket_thuc = fields.Date(string='Ngày Kết Thúc')
    
    tien_do_du_an = fields.Selection([
        ('chua_bat_dau', 'Chưa Bắt Đầu'),
        ('dang_thuc_hien', 'Đang Thực Hiện'),
        ('hoan_thanh', 'Hoàn Thành'),
        ('tam_dung', 'Tạm Dừng')
    ], string="Trạng Thái Dự Án", compute='_compute_tien_do_du_an', store=True, default='chua_bat_dau')
    phan_tram_du_an = fields.Float(string="Tiến Độ Dự Án (%)", default=0.0, readonly=True)

    @api.depends('ngay_bat_dau', 'ngay_ket_thuc', 'phan_tram_du_an')
    def _compute_tien_do_du_an(self):
        """Tự động cập nhật trạng thái dự án theo thời gian và tiến độ"""
        today = date.today()
        for record in self:
            if not record.ngay_bat_dau:
                record.tien_do_du_an = 'chua_bat_dau'
            elif today < record.ngay_bat_dau:
                # Chưa đến ngày bắt đầu
                record.tien_do_du_an = 'chua_bat_dau'
            elif record.ngay_ket_thuc and today > record.ngay_ket_thuc:
                # Đã qua ngày kết thúc - kiểm tra xem đã hoàn thành chưa
                if record.phan_tram_du_an >= 100:
                    record.tien_do_du_an = 'hoan_thanh'
                else:
                    record.tien_do_du_an = 'dang_thuc_hien'
            else:
                # Đang trong thời gian thực hiện
                record.tien_do_du_an = 'dang_thuc_hien'

    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_ngay_thang(self):
        """Kiểm tra tính hợp lệ của ngày tháng"""
        for record in self:
            if record.ngay_ket_thuc and record.ngay_bat_dau:
                if record.ngay_ket_thuc < record.ngay_bat_dau:
                    raise ValidationError("Ngày kết thúc không thể sớm hơn ngày bắt đầu.")

    @api.model
    def create(self, vals):
        """ Đảm bảo người phụ trách có trong danh sách nhân viên tham gia khi tạo dự án """
        nguoi_phu_trach_id = vals.get('nguoi_phu_trach_id')
        nhan_vien_ids = vals.get('nhan_vien_ids', [(6, 0, [])])  # Mặc định là danh sách rỗng nếu không có

        if nguoi_phu_trach_id:
            # Lấy danh sách nhân viên hiện có
            nhan_vien_list = set(nhan_vien_ids[0][2]) if nhan_vien_ids else set()
            # Thêm người phụ trách vào danh sách
            nhan_vien_list.add(nguoi_phu_trach_id)
            vals['nhan_vien_ids'] = [(6, 0, list(nhan_vien_list))]

        record = super(DuAn, self).create(vals)
        # Tự động tính toán trạng thái sau khi tạo
        record._compute_tien_do_du_an()
        return record

    def write(self, vals):
        """ Đảm bảo người phụ trách có trong danh sách nhân viên tham gia khi cập nhật dự án """
        for record in self:
            nguoi_phu_trach_id = vals.get('nguoi_phu_trach_id', record.nguoi_phu_trach_id.id if record.nguoi_phu_trach_id else False)
            nhan_vien_ids = vals.get('nhan_vien_ids', [(6, 0, record.nhan_vien_ids.ids)])

            if nguoi_phu_trach_id:
                nhan_vien_list = set(nhan_vien_ids[0][2]) if nhan_vien_ids else set()
                nhan_vien_list.add(nguoi_phu_trach_id)
                vals['nhan_vien_ids'] = [(6, 0, list(nhan_vien_list))]

        result = super(DuAn, self).write(vals)
        # Trạng thái sẽ tự động được tính toán vì tien_do_du_an là computed field
        # Chỉ cần đảm bảo computed field được trigger khi ngày tháng thay đổi
        return result

    def _compute_phan_tram_du_an(self):
        """Tính phần trăm hoàn thành dự án theo số công việc đã hoàn thành
        Method này được gọi thủ công từ module quan_ly_cong_viec khi có thay đổi công việc
        Trạng thái dự án sẽ tự động được tính toán vì tien_do_du_an là computed field
        """
        for record in self:
            # Tìm tất cả công việc thuộc dự án này
            cong_viec_ids = self.env['cong_viec'].search([('du_an_id', '=', record.id)])
            
            if cong_viec_ids:
                # Đếm số công việc đã hoàn thành (phan_tram_cong_viec >= 100)
                so_cong_viec_hoan_thanh = len(cong_viec_ids.filtered(lambda cv: cv.phan_tram_cong_viec >= 100.0))
                tong_so_cong_viec = len(cong_viec_ids)
                
                # Tính phần trăm: (số công việc hoàn thành / tổng số công việc) * 100
                if tong_so_cong_viec > 0:
                    record.phan_tram_du_an = (so_cong_viec_hoan_thanh / tong_so_cong_viec) * 100.0
                else:
                    record.phan_tram_du_an = 0.0
            else:
                record.phan_tram_du_an = 0.0

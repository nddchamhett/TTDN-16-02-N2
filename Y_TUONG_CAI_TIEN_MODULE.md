# 💡 Ý TƯỞNG CẢI TIẾN MODULE NHÂN SỰ VÀ QUẢN LÝ DỰ ÁN

## 🎯 MODULE NHÂN SỰ (nhan_su)

### 1. QUẢN LÝ HỢP ĐỒNG LAO ĐỘNG

#### Tính năng:
- Lưu thông tin hợp đồng (loại, ngày ký, ngày hết hạn)
- Cảnh báo hợp đồng sắp hết hạn (30 ngày trước)
- Lịch sử gia hạn hợp đồng
- Tính thâm niên tự động

#### Model mới:
```python
class HopDongLaoDong(models.Model):
    _name = 'nhan_su.hop_dong_lao_dong'
    _description = 'Hợp đồng lao động'
    
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Thử việc'),
        ('xac_dinh', 'Xác định thời hạn'),
        ('khong_xac_dinh', 'Không xác định thời hạn'),
        ('mua_vu', 'Mùa vụ')
    ], required=True)
    ngay_ky = fields.Date('Ngày ký', required=True)
    ngay_het_han = fields.Date('Ngày hết hạn')
    luong_co_ban = fields.Float('Lương cơ bản')
    trang_thai = fields.Selection([
        ('dang_hieu_luc', 'Đang hiệu lực'),
        ('het_han', 'Hết hạn'),
        ('da_thanh_ly', 'Đã thanh lý')
    ], compute='_compute_trang_thai', store=True)
    
    so_ngay_con_lai = fields.Integer('Số ngày còn lại', compute='_compute_ngay_con_lai')
    canh_bao = fields.Boolean('Cảnh báo', compute='_compute_canh_bao')
    
    @api.depends('ngay_het_han')
    def _compute_ngay_con_lai(self):
        today = fields.Date.today()
        for record in self:
            if record.ngay_het_han:
                delta = record.ngay_het_han - today
                record.so_ngay_con_lai = delta.days
            else:
                record.so_ngay_con_lai = 0
    
    @api.depends('so_ngay_con_lai')
    def _compute_canh_bao(self):
        for record in self:
            record.canh_bao = 0 < record.so_ngay_con_lai <= 30
```

**Lợi ích**:
- ✅ Quản lý chặt chẽ hợp đồng
- ✅ Tránh quên gia hạn
- ✅ Báo cáo thâm niên chính xác

---

### 2. QUẢN LÝ CHẤM CÔNG VÀ NGHỈ PHÉP

#### Tính năng:
- Đăng ký nghỉ phép online
- Duyệt nghỉ phép (workflow)
- Tính số ngày phép còn lại
- Lịch sử chấm công
- Báo cáo đi muộn, về sớm

#### Model mới:
```python
class NghiPhep(models.Model):
    _name = 'nhan_su.nghi_phep'
    _description = 'Đơn nghỉ phép'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    loai_phep = fields.Selection([
        ('phep_nam', 'Phép năm'),
        ('om', 'Ốm'),
        ('khong_luong', 'Không lương'),
        ('hieu', 'Hiếu'),
        ('ho', 'Hỷ')
    ], required=True)
    ngay_bat_dau = fields.Date('Từ ngày', required=True)
    ngay_ket_thuc = fields.Date('Đến ngày', required=True)
    so_ngay = fields.Float('Số ngày', compute='_compute_so_ngay', store=True)
    ly_do = fields.Text('Lý do')
    
    trang_thai = fields.Selection([
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('tu_choi', 'Từ chối')
    ], default='cho_duyet', tracking=True)
    
    nguoi_duyet_id = fields.Many2one('nhan_su.nhan_vien', 'Người duyệt')
    ngay_duyet = fields.Datetime('Ngày duyệt')
    
    @api.depends('ngay_bat_dau', 'ngay_ket_thuc')
    def _compute_so_ngay(self):
        for record in self:
            if record.ngay_bat_dau and record.ngay_ket_thuc:
                delta = record.ngay_ket_thuc - record.ngay_bat_dau
                record.so_ngay = delta.days + 1
    
    def action_duyet(self):
        self.write({
            'trang_thai': 'da_duyet',
            'nguoi_duyet_id': self.env.user.employee_id.id,
            'ngay_duyet': fields.Datetime.now()
        })
        # Gửi email thông báo
        self.message_post(
            body=f"Đơn nghỉ phép đã được duyệt bởi {self.nguoi_duyet_id.ho_va_ten}",
            subject="Duyệt nghỉ phép"
        )

class ChamCong(models.Model):
    _name = 'nhan_su.cham_cong'
    _description = 'Chấm công'
    
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    ngay = fields.Date('Ngày', required=True, default=fields.Date.today)
    gio_vao = fields.Datetime('Giờ vào')
    gio_ra = fields.Datetime('Giờ ra')
    so_gio_lam = fields.Float('Số giờ làm', compute='_compute_so_gio')
    di_muon = fields.Boolean('Đi muộn', compute='_compute_di_muon')
    ve_som = fields.Boolean('Về sớm', compute='_compute_ve_som')
    
    @api.depends('gio_vao', 'gio_ra')
    def _compute_so_gio(self):
        for record in self:
            if record.gio_vao and record.gio_ra:
                delta = record.gio_ra - record.gio_vao
                record.so_gio_lam = delta.total_seconds() / 3600
```

**Lợi ích**:
- ✅ Tự động hóa quy trình nghỉ phép
- ✅ Giảm công việc thủ công
- ✅ Báo cáo chính xác

---

### 3. ĐÁNH GIÁ NĂNG LỰC VÀ KPI

#### Tính năng:
- Thiết lập KPI cho từng vị trí
- Đánh giá định kỳ (tháng/quý/năm)
- Xếp hạng nhân viên
- Lịch sử đánh giá
- Biểu đồ phát triển

#### Model mới:
```python
class KPI(models.Model):
    _name = 'nhan_su.kpi'
    _description = 'Chỉ tiêu KPI'
    
    ten_kpi = fields.Char('Tên KPI', required=True)
    chuc_vu_id = fields.Many2one('nhan_su.chuc_vu', 'Áp dụng cho chức vụ')
    trong_so = fields.Float('Trọng số (%)', default=100)
    mo_ta = fields.Text('Mô tả')
    cach_tinh = fields.Text('Cách tính')

class DanhGiaNangLuc(models.Model):
    _name = 'nhan_su.danh_gia_nang_luc'
    _description = 'Đánh giá năng lực'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    ky_danh_gia = fields.Selection([
        ('thang', 'Tháng'),
        ('quy', 'Quý'),
        ('nam', 'Năm')
    ], required=True)
    thang = fields.Selection([(str(i), str(i)) for i in range(1, 13)], 'Tháng')
    nam = fields.Integer('Năm', default=lambda self: fields.Date.today().year)
    
    chi_tiet_ids = fields.One2many('nhan_su.danh_gia_chi_tiet', 'danh_gia_id', 'Chi tiết')
    tong_diem = fields.Float('Tổng điểm', compute='_compute_tong_diem', store=True)
    xep_loai = fields.Selection([
        ('xuat_sac', 'Xuất sắc'),
        ('tot', 'Tốt'),
        ('kha', 'Khá'),
        ('trung_binh', 'Trung bình'),
        ('yeu', 'Yếu')
    ], compute='_compute_xep_loai', store=True)
    
    nguoi_danh_gia_id = fields.Many2one('nhan_su.nhan_vien', 'Người đánh giá')
    nhan_xet = fields.Text('Nhận xét')
    
    @api.depends('chi_tiet_ids.diem_dat_duoc')
    def _compute_tong_diem(self):
        for record in self:
            record.tong_diem = sum(record.chi_tiet_ids.mapped('diem_dat_duoc'))
    
    @api.depends('tong_diem')
    def _compute_xep_loai(self):
        for record in self:
            if record.tong_diem >= 90:
                record.xep_loai = 'xuat_sac'
            elif record.tong_diem >= 80:
                record.xep_loai = 'tot'
            elif record.tong_diem >= 70:
                record.xep_loai = 'kha'
            elif record.tong_diem >= 50:
                record.xep_loai = 'trung_binh'
            else:
                record.xep_loai = 'yeu'

class DanhGiaChiTiet(models.Model):
    _name = 'nhan_su.danh_gia_chi_tiet'
    _description = 'Chi tiết đánh giá'
    
    danh_gia_id = fields.Many2one('nhan_su.danh_gia_nang_luc', required=True, ondelete='cascade')
    kpi_id = fields.Many2one('nhan_su.kpi', 'KPI', required=True)
    trong_so = fields.Float(related='kpi_id.trong_so', string='Trọng số')
    diem_dat_duoc = fields.Float('Điểm đạt được')
    ghi_chu = fields.Text('Ghi chú')
```

**Lợi ích**:
- ✅ Đánh giá khách quan
- ✅ Theo dõi phát triển nhân viên
- ✅ Cơ sở cho tăng lương, thưởng

---

### 4. QUẢN LÝ ĐÀO TẠO

#### Tính năng:
- Kế hoạch đào tạo
- Đăng ký khóa học
- Theo dõi tiến độ học
- Chứng chỉ sau đào tạo
- Chi phí đào tạo

#### Model mới:
```python
class KhoaHoc(models.Model):
    _name = 'nhan_su.khoa_hoc'
    _description = 'Khóa học đào tạo'
    
    ten_khoa_hoc = fields.Char('Tên khóa học', required=True)
    loai_khoa_hoc = fields.Selection([
        ('noi_bo', 'Nội bộ'),
        ('ben_ngoai', 'Bên ngoài')
    ], required=True)
    ngay_bat_dau = fields.Date('Ngày bắt đầu')
    ngay_ket_thuc = fields.Date('Ngày kết thúc')
    dia_diem = fields.Char('Địa điểm')
    giang_vien = fields.Char('Giảng viên')
    chi_phi = fields.Float('Chi phí')
    so_hoc_vien = fields.Integer('Số học viên', compute='_compute_so_hoc_vien')
    
    hoc_vien_ids = fields.One2many('nhan_su.hoc_vien', 'khoa_hoc_id', 'Học viên')
    
    @api.depends('hoc_vien_ids')
    def _compute_so_hoc_vien(self):
        for record in self:
            record.so_hoc_vien = len(record.hoc_vien_ids)

class HocVien(models.Model):
    _name = 'nhan_su.hoc_vien'
    _description = 'Học viên'
    
    khoa_hoc_id = fields.Many2one('nhan_su.khoa_hoc', required=True, ondelete='cascade')
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    trang_thai = fields.Selection([
        ('dang_ky', 'Đăng ký'),
        ('dang_hoc', 'Đang học'),
        ('hoan_thanh', 'Hoàn thành'),
        ('bo_hoc', 'Bỏ học')
    ], default='dang_ky')
    diem_so = fields.Float('Điểm số')
    nhan_xet = fields.Text('Nhận xét')
    chung_chi_id = fields.Many2one('nhan_su.chung_chi_bang_cap', 'Chứng chỉ nhận được')
```

**Lợi ích**:
- ✅ Nâng cao năng lực nhân viên
- ✅ Quản lý chi phí đào tạo
- ✅ Theo dõi hiệu quả đào tạo

---

### 5. QUẢN LÝ LƯƠNG THƯỞNG

#### Tính năng:
- Bảng lương theo tháng
- Tính lương tự động (lương cơ bản + phụ cấp + thưởng - khấu trừ)
- Phụ cấp (ăn trưa, xăng xe, điện thoại...)
- Thưởng (KPI, dự án, lễ tết...)
- Khấu trừ (BHXH, thuế, phạt...)
- Phiếu lương

#### Model mới:
```python
class BangLuong(models.Model):
    _name = 'nhan_su.bang_luong'
    _description = 'Bảng lương'
    
    thang = fields.Selection([(str(i), str(i)) for i in range(1, 13)], required=True)
    nam = fields.Integer('Năm', required=True, default=lambda self: fields.Date.today().year)
    trang_thai = fields.Selection([
        ('nhap', 'Đang nhập'),
        ('duyet', 'Đã duyệt'),
        ('chi_tra', 'Đã chi trả')
    ], default='nhap')
    
    chi_tiet_ids = fields.One2many('nhan_su.chi_tiet_luong', 'bang_luong_id', 'Chi tiết')
    tong_luong = fields.Float('Tổng lương', compute='_compute_tong_luong')
    
    @api.depends('chi_tiet_ids.luong_thuc_nhan')
    def _compute_tong_luong(self):
        for record in self:
            record.tong_luong = sum(record.chi_tiet_ids.mapped('luong_thuc_nhan'))
    
    def action_tinh_luong_tu_dong(self):
        """Tính lương tự động cho tất cả nhân viên"""
        NhanVien = self.env['nhan_su.nhan_vien']
        for nv in NhanVien.search([]):
            # Lấy hợp đồng hiện tại
            hop_dong = self.env['nhan_su.hop_dong_lao_dong'].search([
                ('nhan_vien_id', '=', nv.id),
                ('trang_thai', '=', 'dang_hieu_luc')
            ], limit=1)
            
            if hop_dong:
                self.env['nhan_su.chi_tiet_luong'].create({
                    'bang_luong_id': self.id,
                    'nhan_vien_id': nv.id,
                    'luong_co_ban': hop_dong.luong_co_ban,
                })

class ChiTietLuong(models.Model):
    _name = 'nhan_su.chi_tiet_luong'
    _description = 'Chi tiết lương'
    
    bang_luong_id = fields.Many2one('nhan_su.bang_luong', required=True, ondelete='cascade')
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    
    # Lương
    luong_co_ban = fields.Float('Lương cơ bản')
    phu_cap_an_trua = fields.Float('Phụ cấp ăn trưa')
    phu_cap_xang_xe = fields.Float('Phụ cấp xăng xe')
    phu_cap_dien_thoai = fields.Float('Phụ cấp điện thoại')
    thuong_kpi = fields.Float('Thưởng KPI')
    thuong_du_an = fields.Float('Thưởng dự án')
    
    # Khấu trừ
    bhxh = fields.Float('BHXH (8%)', compute='_compute_bhxh')
    bhyt = fields.Float('BHYT (1.5%)', compute='_compute_bhyt')
    bhtn = fields.Float('BHTN (1%)', compute='_compute_bhtn')
    thue_tncn = fields.Float('Thuế TNCN')
    phat = fields.Float('Phạt')
    
    # Tổng
    tong_thu_nhap = fields.Float('Tổng thu nhập', compute='_compute_tong')
    tong_khau_tru = fields.Float('Tổng khấu trừ', compute='_compute_tong')
    luong_thuc_nhan = fields.Float('Lương thực nhận', compute='_compute_tong')
    
    @api.depends('luong_co_ban')
    def _compute_bhxh(self):
        for record in self:
            record.bhxh = record.luong_co_ban * 0.08
    
    @api.depends('luong_co_ban')
    def _compute_bhyt(self):
        for record in self:
            record.bhyt = record.luong_co_ban * 0.015
    
    @api.depends('luong_co_ban')
    def _compute_bhtn(self):
        for record in self:
            record.bhtn = record.luong_co_ban * 0.01
    
    @api.depends('luong_co_ban', 'phu_cap_an_trua', 'phu_cap_xang_xe', 
                 'phu_cap_dien_thoai', 'thuong_kpi', 'thuong_du_an',
                 'bhxh', 'bhyt', 'bhtn', 'thue_tncn', 'phat')
    def _compute_tong(self):
        for record in self:
            record.tong_thu_nhap = (
                record.luong_co_ban + 
                record.phu_cap_an_trua + 
                record.phu_cap_xang_xe +
                record.phu_cap_dien_thoai + 
                record.thuong_kpi + 
                record.thuong_du_an
            )
            record.tong_khau_tru = (
                record.bhxh + 
                record.bhyt + 
                record.bhtn + 
                record.thue_tncn + 
                record.phat
            )
            record.luong_thuc_nhan = record.tong_thu_nhap - record.tong_khau_tru
```

**Lợi ích**:
- ✅ Tự động hóa tính lương
- ✅ Minh bạch thu nhập
- ✅ Giảm sai sót

---

## 🎯 MODULE QUẢN LÝ DỰ ÁN (quan_ly_du_an)

### 1. QUẢN LÝ RỦI RO DỰ ÁN

#### Tính năng:
- Nhận diện rủi ro
- Đánh giá mức độ rủi ro (xác suất x tác động)
- Kế hoạch ứng phó
- Theo dõi rủi ro
- Ma trận rủi ro

#### Model mới:
```python
class RuiRo(models.Model):
    _name = 'quan_ly_du_an.rui_ro'
    _description = 'Rủi ro dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    du_an_id = fields.Many2one('quan_ly_du_an.du_an', required=True, ondelete='cascade')
    ten_rui_ro = fields.Char('Tên rủi ro', required=True)
    mo_ta = fields.Text('Mô tả')
    
    loai_rui_ro = fields.Selection([
        ('ky_thuat', 'Kỹ thuật'),
        ('nhan_su', 'Nhân sự'),
        ('tai_chinh', 'Tài chính'),
        ('phap_ly', 'Pháp lý'),
        ('khac', 'Khác')
    ], required=True)
    
    xac_suat = fields.Selection([
        ('1', 'Rất thấp (10%)'),
        ('2', 'Thấp (30%)'),
        ('3', 'Trung bình (50%)'),
        ('4', 'Cao (70%)'),
        ('5', 'Rất cao (90%)')
    ], 'Xác suất', required=True)
    
    tac_dong = fields.Selection([
        ('1', 'Rất thấp'),
        ('2', 'Thấp'),
        ('3', 'Trung bình'),
        ('4', 'Cao'),
        ('5', 'Rất cao')
    ], 'Tác động', required=True)
    
    muc_do_rui_ro = fields.Integer('Mức độ rủi ro', compute='_compute_muc_do', store=True)
    mau_sac = fields.Char('Màu sắc', compute='_compute_mau_sac')
    
    ke_hoach_ung_pho = fields.Text('Kế hoạch ứng phó')
    nguoi_phu_trach_id = fields.Many2one('nhan_su.nhan_vien', 'Người phụ trách')
    
    trang_thai = fields.Selection([
        ('nhan_dien', 'Nhận diện'),
        ('dang_theo_doi', 'Đang theo dõi'),
        ('da_xay_ra', 'Đã xảy ra'),
        ('da_giai_quyet', 'Đã giải quyết')
    ], default='nhan_dien', tracking=True)
    
    @api.depends('xac_suat', 'tac_dong')
    def _compute_muc_do(self):
        for record in self:
            xs = int(record.xac_suat or '0')
            td = int(record.tac_dong or '0')
            record.muc_do_rui_ro = xs * td
    
    @api.depends('muc_do_rui_ro')
    def _compute_mau_sac(self):
        for record in self:
            if record.muc_do_rui_ro >= 15:
                record.mau_sac = 'red'  # Rủi ro cao
            elif record.muc_do_rui_ro >= 8:
                record.mau_sac = 'orange'  # Rủi ro trung bình
            else:
                record.mau_sac = 'green'  # Rủi ro thấp
```

**Lợi ích**:
- ✅ Chủ động phòng ngừa
- ✅ Giảm thiểu tổn thất
- ✅ Tăng tỷ lệ thành công

---

### 2. QUẢN LÝ VẤN ĐỀ (ISSUE TRACKING)

#### Tính năng:
- Báo cáo vấn đề
- Phân loại mức độ (Critical, High, Medium, Low)
- Gán người xử lý
- Theo dõi tiến độ
- Liên kết với công việc

#### Model mới:
```python
class VanDe(models.Model):
    _name = 'quan_ly_du_an.van_de'
    _description = 'Vấn đề dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    du_an_id = fields.Many2one('quan_ly_du_an.du_an', required=True)
    cong_viec_id = fields.Many2one('quan_ly_cong_viec.cong_viec', 'Công việc liên quan')
    
    tieu_de = fields.Char('Tiêu đề', required=True)
    mo_ta = fields.Html('Mô tả')
    
    loai_van_de = fields.Selection([
        ('bug', 'Bug'),
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement'),
        ('question', 'Question')
    ], required=True)
    
    muc_do = fields.Selection([
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], required=True, default='medium')
    
    nguoi_bao_cao_id = fields.Many2one('nhan_su.nhan_vien', 'Người báo cáo', 
                                        default=lambda self: self.env.user.employee_id)
    nguoi_xu_ly_id = fields.Many2one('nhan_su.nhan_vien', 'Người xử lý')
    
    trang_thai = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], default='open', tracking=True)
    
    ngay_bao_cao = fields.Datetime('Ngày báo cáo', default=fields.Datetime.now)
    ngay_giai_quyet = fields.Datetime('Ngày giải quyết')
    
    thoi_gian_xu_ly = fields.Float('Thời gian xử lý (giờ)', compute='_compute_thoi_gian')
    
    @api.depends('ngay_bao_cao', 'ngay_giai_quyet')
    def _compute_thoi_gian(self):
        for record in self:
            if record.ngay_bao_cao and record.ngay_giai_quyet:
                delta = record.ngay_giai_quyet - record.ngay_bao_cao
                record.thoi_gian_xu_ly = delta.total_seconds() / 3600
```

**Lợi ích**:
- ✅ Phát hiện vấn đề sớm
- ✅ Xử lý nhanh chóng
- ✅ Tránh ảnh hưởng dự án

---

Tiếp tục phần 2...


### 3. QUẢN LÝ TÀI LIỆU DỰ ÁN

#### Tính năng:
- Upload tài liệu (thiết kế, tài liệu kỹ thuật, hợp đồng)
- Phân loại tài liệu
- Phiên bản tài liệu
- Quyền truy cập tài liệu
- Tìm kiếm full-text

#### Model mới:
```python
class TaiLieuDuAn(models.Model):
    _name = 'quan_ly_du_an.tai_lieu'
    _description = 'Tài liệu dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    du_an_id = fields.Many2one('quan_ly_du_an.du_an', required=True, ondelete='cascade')
    ten_tai_lieu = fields.Char('Tên tài liệu', required=True)
    
    loai_tai_lieu = fields.Selection([
        ('thiet_ke', 'Thiết kế'),
        ('ky_thuat', 'Tài liệu kỹ thuật'),
        ('hop_dong', 'Hợp đồng'),
        ('bao_cao', 'Báo cáo'),
        ('khac', 'Khác')
    ], required=True)
    
    file_dinh_kem = fields.Binary('File đính kèm')
    file_name = fields.Char('Tên file')
    
    phien_ban = fields.Char('Phiên bản', default='1.0')
    tai_lieu_goc_id = fields.Many2one('quan_ly_du_an.tai_lieu', 'Tài liệu gốc')
    phien_ban_ids = fields.One2many('quan_ly_du_an.tai_lieu', 'tai_lieu_goc_id', 'Các phiên bản')
    
    nguoi_upload_id = fields.Many2one('nhan_su.nhan_vien', 'Người upload',
                                       default=lambda self: self.env.user.employee_id)
    ngay_upload = fields.Datetime('Ngày upload', default=fields.Datetime.now)
    
    mo_ta = fields.Text('Mô tả')
    tag_ids = fields.Many2many('quan_ly_du_an.tag', string='Tags')
    
    # Quyền truy cập
    public = fields.Boolean('Công khai', default=False)
    nhom_truy_cap_ids = fields.Many2many('res.groups', string='Nhóm được xem')
    
    def action_tao_phien_ban_moi(self):
        """Tạo phiên bản mới của tài liệu"""
        new_version = self.copy({
            'tai_lieu_goc_id': self.tai_lieu_goc_id.id or self.id,
            'phien_ban': self._tang_phien_ban(self.phien_ban),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'quan_ly_du_an.tai_lieu',
            'res_id': new_version.id,
            'view_mode': 'form',
        }
    
    def _tang_phien_ban(self, phien_ban):
        """Tăng số phiên bản: 1.0 → 1.1 → 2.0"""
        parts = phien_ban.split('.')
        minor = int(parts[1]) + 1
        if minor >= 10:
            return f"{int(parts[0]) + 1}.0"
        return f"{parts[0]}.{minor}"

class Tag(models.Model):
    _name = 'quan_ly_du_an.tag'
    _description = 'Tag tài liệu'
    
    name = fields.Char('Tag', required=True)
    color = fields.Integer('Màu')
```

**Lợi ích**:
- ✅ Tập trung tài liệu
- ✅ Quản lý phiên bản
- ✅ Bảo mật thông tin

---

### 4. QUẢN LÝ CUỘC HỌP

#### Tính năng:
- Lên lịch họp
- Gửi thông báo tự động
- Ghi biên bản
- Theo dõi action items
- Tích hợp calendar

#### Model mới:
```python
class CuocHop(models.Model):
    _name = 'quan_ly_du_an.cuoc_hop'
    _description = 'Cuộc họp dự án'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    du_an_id = fields.Many2one('quan_ly_du_an.du_an', required=True)
    tieu_de = fields.Char('Tiêu đề', required=True)
    
    thoi_gian_bat_dau = fields.Datetime('Thời gian bắt đầu', required=True)
    thoi_gian_ket_thuc = fields.Datetime('Thời gian kết thúc', required=True)
    dia_diem = fields.Char('Địa điểm')
    link_online = fields.Char('Link họp online')
    
    chu_tri_id = fields.Many2one('nhan_su.nhan_vien', 'Chủ trì')
    thanh_vien_ids = fields.Many2many('nhan_su.nhan_vien', string='Thành viên tham dự')
    
    noi_dung = fields.Html('Nội dung cuộc họp')
    bien_ban = fields.Html('Biên bản')
    
    action_item_ids = fields.One2many('quan_ly_du_an.action_item', 'cuoc_hop_id', 'Action Items')
    
    trang_thai = fields.Selection([
        ('du_kien', 'Dự kiến'),
        ('dang_dien_ra', 'Đang diễn ra'),
        ('ket_thuc', 'Kết thúc'),
        ('huy', 'Hủy')
    ], default='du_kien', tracking=True)
    
    def action_gui_thong_bao(self):
        """Gửi email thông báo cho thành viên"""
        for thanh_vien in self.thanh_vien_ids:
            if thanh_vien.email:
                self.message_post(
                    body=f"""
                    <p>Kính gửi {thanh_vien.ho_va_ten},</p>
                    <p>Bạn được mời tham dự cuộc họp:</p>
                    <ul>
                        <li>Tiêu đề: {self.tieu_de}</li>
                        <li>Thời gian: {self.thoi_gian_bat_dau}</li>
                        <li>Địa điểm: {self.dia_diem or self.link_online}</li>
                    </ul>
                    """,
                    subject=f"Thông báo cuộc họp: {self.tieu_de}",
                    partner_ids=[thanh_vien.user_id.partner_id.id]
                )

class ActionItem(models.Model):
    _name = 'quan_ly_du_an.action_item'
    _description = 'Action Item từ cuộc họp'
    
    cuoc_hop_id = fields.Many2one('quan_ly_du_an.cuoc_hop', required=True, ondelete='cascade')
    noi_dung = fields.Text('Nội dung', required=True)
    nguoi_phu_trach_id = fields.Many2one('nhan_su.nhan_vien', 'Người phụ trách')
    han_hoan_thanh = fields.Date('Hạn hoàn thành')
    trang_thai = fields.Selection([
        ('chua_lam', 'Chưa làm'),
        ('dang_lam', 'Đang làm'),
        ('hoan_thanh', 'Hoàn thành')
    ], default='chua_lam')
```

**Lợi ích**:
- ✅ Tổ chức họp hiệu quả
- ✅ Theo dõi quyết định
- ✅ Đảm bảo thực hiện action items

---

### 5. BÁO CÁO TIẾN ĐỘ TỰ ĐỘNG

#### Tính năng:
- Tạo báo cáo tự động (hàng ngày/tuần/tháng)
- Gửi email báo cáo
- Biểu đồ tiến độ
- So sánh kế hoạch vs thực tế
- Export PDF

#### Model mới:
```python
class BaoCaoTienDo(models.Model):
    _name = 'quan_ly_du_an.bao_cao_tien_do'
    _description = 'Báo cáo tiến độ dự án'
    
    du_an_id = fields.Many2one('quan_ly_du_an.du_an', required=True)
    
    loai_bao_cao = fields.Selection([
        ('ngay', 'Hàng ngày'),
        ('tuan', 'Hàng tuần'),
        ('thang', 'Hàng tháng'),
        ('quy', 'Hàng quý')
    ], required=True)
    
    tu_ngay = fields.Date('Từ ngày', required=True)
    den_ngay = fields.Date('Đến ngày', required=True)
    
    # Thống kê tự động
    tien_do_ke_hoach = fields.Float('Tiến độ kế hoạch', compute='_compute_tien_do_ke_hoach')
    tien_do_thuc_te = fields.Float('Tiến độ thực tế', compute='_compute_tien_do_thuc_te')
    chenh_lech = fields.Float('Chênh lệch', compute='_compute_chenh_lech')
    
    tong_cong_viec = fields.Integer('Tổng công việc', compute='_compute_thong_ke')
    cong_viec_hoan_thanh = fields.Integer('Công việc hoàn thành', compute='_compute_thong_ke')
    cong_viec_tre_han = fields.Integer('Công việc trễ hạn', compute='_compute_thong_ke')
    
    noi_dung = fields.Html('Nội dung báo cáo')
    
    @api.depends('du_an_id', 'den_ngay')
    def _compute_tien_do_ke_hoach(self):
        """Tính tiến độ theo kế hoạch"""
        for record in self:
            if record.du_an_id and record.den_ngay:
                tong_ngay = (record.du_an_id.ngay_ket_thuc - record.du_an_id.ngay_bat_dau).days
                ngay_da_qua = (record.den_ngay - record.du_an_id.ngay_bat_dau).days
                record.tien_do_ke_hoach = (ngay_da_qua / tong_ngay) * 100 if tong_ngay > 0 else 0
    
    @api.depends('du_an_id')
    def _compute_tien_do_thuc_te(self):
        for record in self:
            record.tien_do_thuc_te = record.du_an_id.tien_do
    
    @api.depends('tien_do_ke_hoach', 'tien_do_thuc_te')
    def _compute_chenh_lech(self):
        for record in self:
            record.chenh_lech = record.tien_do_thuc_te - record.tien_do_ke_hoach
    
    @api.depends('du_an_id', 'tu_ngay', 'den_ngay')
    def _compute_thong_ke(self):
        for record in self:
            cong_viec_ids = self.env['quan_ly_cong_viec.cong_viec'].search([
                ('du_an_id', '=', record.du_an_id.id),
                ('ngay_bat_dau', '>=', record.tu_ngay),
                ('ngay_bat_dau', '<=', record.den_ngay)
            ])
            record.tong_cong_viec = len(cong_viec_ids)
            record.cong_viec_hoan_thanh = len(cong_viec_ids.filtered(lambda x: x.trang_thai == 'hoan_thanh'))
            record.cong_viec_tre_han = len(cong_viec_ids.filtered(lambda x: x.tre_han))
    
    def action_tao_bao_cao(self):
        """Tạo nội dung báo cáo tự động"""
        self.noi_dung = f"""
        <h2>BÁO CÁO TIẾN ĐỘ DỰ ÁN</h2>
        <h3>{self.du_an_id.ten_du_an}</h3>
        <p>Từ ngày {self.tu_ngay} đến {self.den_ngay}</p>
        
        <h4>1. Tổng quan</h4>
        <ul>
            <li>Tiến độ kế hoạch: {self.tien_do_ke_hoach:.1f}%</li>
            <li>Tiến độ thực tế: {self.tien_do_thuc_te:.1f}%</li>
            <li>Chênh lệch: {self.chenh_lech:+.1f}%</li>
        </ul>
        
        <h4>2. Công việc</h4>
        <ul>
            <li>Tổng số: {self.tong_cong_viec}</li>
            <li>Hoàn thành: {self.cong_viec_hoan_thanh}</li>
            <li>Trễ hạn: {self.cong_viec_tre_han}</li>
        </ul>
        """
    
    def action_gui_email(self):
        """Gửi báo cáo qua email"""
        self.action_tao_bao_cao()
        # Gửi cho quản lý dự án
        if self.du_an_id.quan_ly_du_an_id.email:
            self.message_post(
                body=self.noi_dung,
                subject=f"Báo cáo tiến độ: {self.du_an_id.ten_du_an}",
                partner_ids=[self.du_an_id.quan_ly_du_an_id.user_id.partner_id.id]
            )
```

**Lợi ích**:
- ✅ Tiết kiệm thời gian báo cáo
- ✅ Thông tin chính xác, real-time
- ✅ Phát hiện sớm vấn đề

---

### 6. GANTT CHART

#### Tính năng:
- Hiển thị timeline dự án
- Drag & drop để thay đổi thời gian
- Hiển thị phụ thuộc giữa các task
- Zoom in/out timeline
- Export hình ảnh

#### View mới:
```xml
<record id="view_du_an_gantt" model="ir.ui.view">
    <field name="name">quan_ly_du_an.du_an.gantt</field>
    <field name="model">quan_ly_cong_viec.cong_viec</field>
    <field name="arch" type="xml">
        <gantt 
            date_start="ngay_bat_dau"
            date_stop="ngay_ket_thuc"
            default_group_by="du_an_id"
            color="uu_tien"
            progress="tien_do">
            <field name="nguoi_thuc_hien_id"/>
            <field name="trang_thai"/>
        </gantt>
    </field>
</record>
```

**Lợi ích**:
- ✅ Trực quan hóa timeline
- ✅ Dễ dàng điều chỉnh kế hoạch
- ✅ Nhìn thấy phụ thuộc

---

### 7. RESOURCE ALLOCATION (PHÂN BỔ TÀI NGUYÊN)

#### Tính năng:
- Xem workload của nhân viên
- Cảnh báo quá tải
- Tối ưu phân công
- Lịch làm việc
- Capacity planning

#### Model mới:
```python
class PhanBoTaiNguyen(models.Model):
    _name = 'quan_ly_du_an.phan_bo_tai_nguyen'
    _description = 'Phân bổ tài nguyên'
    
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    du_an_id = fields.Many2one('quan_ly_du_an.du_an', required=True)
    
    tu_ngay = fields.Date('Từ ngày', required=True)
    den_ngay = fields.Date('Đến ngày', required=True)
    
    phan_tram_thoi_gian = fields.Float('% Thời gian', default=100,
                                        help='Phần trăm thời gian dành cho dự án này')
    
    so_gio_du_kien = fields.Float('Số giờ dự kiến')
    so_gio_thuc_te = fields.Float('Số giờ thực tế', compute='_compute_so_gio_thuc_te')
    
    @api.depends('nhan_vien_id', 'du_an_id', 'tu_ngay', 'den_ngay')
    def _compute_so_gio_thuc_te(self):
        """Tính số giờ thực tế từ công việc"""
        for record in self:
            cong_viec_ids = self.env['quan_ly_cong_viec.cong_viec'].search([
                ('nguoi_thuc_hien_id', '=', record.nhan_vien_id.id),
                ('du_an_id', '=', record.du_an_id.id),
                ('ngay_bat_dau', '>=', record.tu_ngay),
                ('ngay_bat_dau', '<=', record.den_ngay)
            ])
            record.so_gio_thuc_te = sum(cong_viec_ids.mapped('so_gio_da_lam'))

class WorkloadNhanVien(models.Model):
    _name = 'quan_ly_du_an.workload_nhan_vien'
    _description = 'Workload nhân viên'
    
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    tuan = fields.Integer('Tuần')
    nam = fields.Integer('Năm')
    
    tong_phan_tram = fields.Float('Tổng % phân bổ', compute='_compute_workload')
    qua_tai = fields.Boolean('Quá tải', compute='_compute_qua_tai')
    
    @api.depends('nhan_vien_id', 'tuan', 'nam')
    def _compute_workload(self):
        for record in self:
            # Tính tổng % từ tất cả dự án
            phan_bo_ids = self.env['quan_ly_du_an.phan_bo_tai_nguyen'].search([
                ('nhan_vien_id', '=', record.nhan_vien_id.id),
                # Filter by week/year
            ])
            record.tong_phan_tram = sum(phan_bo_ids.mapped('phan_tram_thoi_gian'))
    
    @api.depends('tong_phan_tram')
    def _compute_qua_tai(self):
        for record in self:
            record.qua_tai = record.tong_phan_tram > 100
```

**Lợi ích**:
- ✅ Tránh quá tải nhân viên
- ✅ Tối ưu sử dụng nguồn lực
- ✅ Cân bằng công việc

---

### 8. TIME TRACKING

#### Tính năng:
- Ghi nhận thời gian làm việc
- Timer tích hợp
- Báo cáo timesheet
- So sánh estimate vs actual
- Tính lương theo giờ

#### Model mới:
```python
class TimeEntry(models.Model):
    _name = 'quan_ly_du_an.time_entry'
    _description = 'Ghi nhận thời gian'
    
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True,
                                     default=lambda self: self.env.user.employee_id)
    du_an_id = fields.Many2one('quan_ly_du_an.du_an', required=True)
    cong_viec_id = fields.Many2one('quan_ly_cong_viec.cong_viec', 'Công việc')
    
    ngay = fields.Date('Ngày', required=True, default=fields.Date.today)
    gio_bat_dau = fields.Datetime('Giờ bắt đầu')
    gio_ket_thuc = fields.Datetime('Giờ kết thúc')
    
    so_gio = fields.Float('Số giờ', compute='_compute_so_gio', store=True)
    mo_ta = fields.Text('Mô tả công việc')
    
    # Timer
    dang_chay = fields.Boolean('Đang chạy', default=False)
    
    @api.depends('gio_bat_dau', 'gio_ket_thuc')
    def _compute_so_gio(self):
        for record in self:
            if record.gio_bat_dau and record.gio_ket_thuc:
                delta = record.gio_ket_thuc - record.gio_bat_dau
                record.so_gio = delta.total_seconds() / 3600
    
    def action_bat_dau_timer(self):
        """Bắt đầu đếm giờ"""
        self.write({
            'gio_bat_dau': fields.Datetime.now(),
            'dang_chay': True
        })
    
    def action_dung_timer(self):
        """Dừng đếm giờ"""
        self.write({
            'gio_ket_thuc': fields.Datetime.now(),
            'dang_chay': False
        })
```

**Lợi ích**:
- ✅ Theo dõi chính xác thời gian
- ✅ Tính lương công bằng
- ✅ Phân tích hiệu suất

---


## 🔗 Ý TƯỞNG TÍCH HỢP GIỮA CÁC MODULES

### 1. DASHBOARD TỔNG HỢP

#### Tính năng:
- Dashboard tổng hợp 3 modules
- Thống kê real-time
- Biểu đồ tương tác
- Drill-down chi tiết
- Responsive design

#### Model mới:
```python
class DashboardTongHop(models.Model):
    _name = 'he_thong.dashboard'
    _description = 'Dashboard tổng hợp'
    
    # Thống kê nhân sự
    tong_nhan_vien = fields.Integer('Tổng nhân viên', compute='_compute_nhan_su')
    nhan_vien_dang_lam = fields.Integer('Đang làm việc', compute='_compute_nhan_su')
    nhan_vien_nghi_phep = fields.Integer('Đang nghỉ phép', compute='_compute_nhan_su')
    
    # Thống kê dự án
    tong_du_an = fields.Integer('Tổng dự án', compute='_compute_du_an')
    du_an_dang_thuc_hien = fields.Integer('Đang thực hiện', compute='_compute_du_an')
    du_an_hoan_thanh = fields.Integer('Hoàn thành', compute='_compute_du_an')
    du_an_tre_han = fields.Integer('Trễ hạn', compute='_compute_du_an')
    
    # Thống kê công việc
    tong_cong_viec = fields.Integer('Tổng công việc', compute='_compute_cong_viec')
    cong_viec_hoan_thanh = fields.Integer('Hoàn thành', compute='_compute_cong_viec')
    cong_viec_dang_lam = fields.Integer('Đang làm', compute='_compute_cong_viec')
    cong_viec_tre_han = fields.Integer('Trễ hạn', compute='_compute_cong_viec')
    
    # Biểu đồ
    bieu_do_du_an = fields.Text('Dữ liệu biểu đồ dự án', compute='_compute_bieu_do')
    bieu_do_nhan_su = fields.Text('Dữ liệu biểu đồ nhân sự', compute='_compute_bieu_do')
    
    @api.depends()
    def _compute_nhan_su(self):
        for record in self:
            NhanVien = self.env['nhan_su.nhan_vien']
            record.tong_nhan_vien = NhanVien.search_count([])
            record.nhan_vien_dang_lam = NhanVien.search_count([('trang_thai', '=', 'dang_lam_viec')])
            
            # Đếm nhân viên đang nghỉ phép hôm nay
            today = fields.Date.today()
            nghi_phep_ids = self.env['nhan_su.nghi_phep'].search([
                ('ngay_bat_dau', '<=', today),
                ('ngay_ket_thuc', '>=', today),
                ('trang_thai', '=', 'da_duyet')
            ])
            record.nhan_vien_nghi_phep = len(nghi_phep_ids.mapped('nhan_vien_id'))
    
    @api.depends()
    def _compute_du_an(self):
        for record in self:
            DuAn = self.env['quan_ly_du_an.du_an']
            record.tong_du_an = DuAn.search_count([])
            record.du_an_dang_thuc_hien = DuAn.search_count([('trang_thai', '=', 'dang_thuc_hien')])
            record.du_an_hoan_thanh = DuAn.search_count([('trang_thai', '=', 'hoan_thanh')])
            
            # Dự án trễ hạn
            today = fields.Date.today()
            record.du_an_tre_han = DuAn.search_count([
                ('trang_thai', '=', 'dang_thuc_hien'),
                ('ngay_ket_thuc', '<', today)
            ])
    
    @api.depends()
    def _compute_cong_viec(self):
        for record in self:
            CongViec = self.env['quan_ly_cong_viec.cong_viec']
            record.tong_cong_viec = CongViec.search_count([])
            record.cong_viec_hoan_thanh = CongViec.search_count([('trang_thai', '=', 'hoan_thanh')])
            record.cong_viec_dang_lam = CongViec.search_count([('trang_thai', '=', 'dang_thuc_hien')])
            record.cong_viec_tre_han = CongViec.search_count([('tre_han', '=', True)])
```

**View Dashboard**:
```xml
<record id="view_dashboard_tong_hop" model="ir.ui.view">
    <field name="name">he_thong.dashboard.form</field>
    <field name="model">he_thong.dashboard</field>
    <field name="arch" type="xml">
        <form string="Dashboard Tổng Hợp">
            <sheet>
                <div class="row">
                    <!-- Nhân sự -->
                    <div class="col-md-4">
                        <div class="card">
                            <h3>Nhân sự</h3>
                            <field name="tong_nhan_vien" widget="statinfo"/>
                            <field name="nhan_vien_dang_lam" widget="statinfo"/>
                            <field name="nhan_vien_nghi_phep" widget="statinfo"/>
                        </div>
                    </div>
                    
                    <!-- Dự án -->
                    <div class="col-md-4">
                        <div class="card">
                            <h3>Dự án</h3>
                            <field name="tong_du_an" widget="statinfo"/>
                            <field name="du_an_dang_thuc_hien" widget="statinfo"/>
                            <field name="du_an_tre_han" widget="statinfo"/>
                        </div>
                    </div>
                    
                    <!-- Công việc -->
                    <div class="col-md-4">
                        <div class="card">
                            <h3>Công việc</h3>
                            <field name="tong_cong_viec" widget="statinfo"/>
                            <field name="cong_viec_hoan_thanh" widget="statinfo"/>
                            <field name="cong_viec_tre_han" widget="statinfo"/>
                        </div>
                    </div>
                </div>
                
                <!-- Biểu đồ -->
                <div class="row">
                    <div class="col-md-6">
                        <field name="bieu_do_du_an" widget="chart"/>
                    </div>
                    <div class="col-md-6">
                        <field name="bieu_do_nhan_su" widget="chart"/>
                    </div>
                </div>
            </sheet>
        </form>
    </field>
</record>
```

**Lợi ích**:
- ✅ Nhìn tổng quan toàn hệ thống
- ✅ Ra quyết định nhanh
- ✅ Phát hiện vấn đề sớm

---

### 2. HỆ THỐNG THÔNG BÁO (NOTIFICATION)

#### Tính năng:
- Thông báo real-time
- Email notification
- SMS notification
- Push notification (mobile)
- Cấu hình thông báo cá nhân

#### Model mới:
```python
class ThongBao(models.Model):
    _name = 'he_thong.thong_bao'
    _description = 'Thông báo hệ thống'
    _order = 'ngay_tao desc'
    
    nguoi_nhan_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    tieu_de = fields.Char('Tiêu đề', required=True)
    noi_dung = fields.Html('Nội dung')
    
    loai_thong_bao = fields.Selection([
        ('cong_viec', 'Công việc'),
        ('du_an', 'Dự án'),
        ('nghi_phep', 'Nghỉ phép'),
        ('hop_dong', 'Hợp đồng'),
        ('he_thong', 'Hệ thống')
    ], required=True)
    
    uu_tien = fields.Selection([
        ('thap', 'Thấp'),
        ('trung_binh', 'Trung bình'),
        ('cao', 'Cao'),
        ('khan_cap', 'Khẩn cấp')
    ], default='trung_binh')
    
    da_doc = fields.Boolean('Đã đọc', default=False)
    ngay_tao = fields.Datetime('Ngày tạo', default=fields.Datetime.now)
    ngay_doc = fields.Datetime('Ngày đọc')
    
    # Link đến record liên quan
    model_lien_quan = fields.Char('Model')
    res_id = fields.Integer('Record ID')
    
    def action_danh_dau_da_doc(self):
        self.write({
            'da_doc': True,
            'ngay_doc': fields.Datetime.now()
        })
    
    def action_mo_record(self):
        """Mở record liên quan"""
        if self.model_lien_quan and self.res_id:
            self.action_danh_dau_da_doc()
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.model_lien_quan,
                'res_id': self.res_id,
                'view_mode': 'form',
            }

class CauHinhThongBao(models.Model):
    _name = 'he_thong.cau_hinh_thong_bao'
    _description = 'Cấu hình thông báo'
    
    nhan_vien_id = fields.Many2one('nhan_su.nhan_vien', required=True)
    
    # Cấu hình theo loại
    thong_bao_cong_viec = fields.Boolean('Thông báo công việc', default=True)
    thong_bao_du_an = fields.Boolean('Thông báo dự án', default=True)
    thong_bao_nghi_phep = fields.Boolean('Thông báo nghỉ phép', default=True)
    
    # Kênh thông báo
    gui_email = fields.Boolean('Gửi email', default=True)
    gui_sms = fields.Boolean('Gửi SMS', default=False)
    gui_push = fields.Boolean('Push notification', default=True)
```

**Tự động tạo thông báo**:
```python
# Trong model cong_viec
def write(self, vals):
    res = super().write(vals)
    
    # Tạo thông báo khi gán công việc
    if 'nguoi_thuc_hien_id' in vals:
        self.env['he_thong.thong_bao'].create({
            'nguoi_nhan_id': vals['nguoi_thuc_hien_id'],
            'tieu_de': f'Bạn được giao công việc mới: {self.ten_cong_viec}',
            'noi_dung': f'<p>Hạn: {self.ngay_ket_thuc}</p>',
            'loai_thong_bao': 'cong_viec',
            'model_lien_quan': 'quan_ly_cong_viec.cong_viec',
            'res_id': self.id,
        })
    
    return res
```

**Lợi ích**:
- ✅ Không bỏ lỡ thông tin quan trọng
- ✅ Phản hồi nhanh
- ✅ Tăng hiệu quả làm việc

---

### 3. MOBILE APP

#### Tính năng:
- Xem thông tin dự án, công việc
- Cập nhật tiến độ
- Chấm công
- Đăng ký nghỉ phép
- Nhận thông báo push

#### API Endpoints:
```python
from odoo import http
from odoo.http import request

class MobileAPI(http.Controller):
    
    @http.route('/api/mobile/login', type='json', auth='none', methods=['POST'])
    def mobile_login(self, username, password):
        """Đăng nhập"""
        uid = request.session.authenticate(request.session.db, username, password)
        if uid:
            user = request.env['res.users'].browse(uid)
            return {
                'success': True,
                'user_id': uid,
                'token': self._generate_token(uid),
                'employee_id': user.employee_id.id,
            }
        return {'success': False, 'message': 'Sai tên đăng nhập hoặc mật khẩu'}
    
    @http.route('/api/mobile/cong_viec', type='json', auth='user', methods=['GET'])
    def get_cong_viec(self):
        """Lấy danh sách công việc của nhân viên"""
        employee = request.env.user.employee_id
        cong_viec_ids = request.env['quan_ly_cong_viec.cong_viec'].search([
            ('nguoi_thuc_hien_id', '=', employee.id),
            ('trang_thai', '!=', 'hoan_thanh')
        ])
        
        return [{
            'id': cv.id,
            'ten_cong_viec': cv.ten_cong_viec,
            'du_an': cv.du_an_id.ten_du_an,
            'tien_do': cv.tien_do,
            'ngay_ket_thuc': cv.ngay_ket_thuc.isoformat() if cv.ngay_ket_thuc else None,
            'uu_tien': cv.uu_tien,
        } for cv in cong_viec_ids]
    
    @http.route('/api/mobile/cap_nhat_tien_do', type='json', auth='user', methods=['POST'])
    def cap_nhat_tien_do(self, cong_viec_id, tien_do, noi_dung):
        """Cập nhật tiến độ công việc"""
        cong_viec = request.env['quan_ly_cong_viec.cong_viec'].browse(cong_viec_id)
        cong_viec.write({'tien_do': tien_do})
        
        # Tạo nhật ký
        request.env['quan_ly_cong_viec.nhat_ky_cong_viec'].create({
            'cong_viec_id': cong_viec_id,
            'noi_dung': noi_dung,
            'tien_do': tien_do,
        })
        
        return {'success': True}
    
    @http.route('/api/mobile/cham_cong', type='json', auth='user', methods=['POST'])
    def cham_cong(self, loai):
        """Chấm công vào/ra"""
        employee = request.env.user.employee_id
        today = fields.Date.today()
        
        cham_cong = request.env['nhan_su.cham_cong'].search([
            ('nhan_vien_id', '=', employee.id),
            ('ngay', '=', today)
        ], limit=1)
        
        if loai == 'vao':
            if not cham_cong:
                cham_cong = request.env['nhan_su.cham_cong'].create({
                    'nhan_vien_id': employee.id,
                    'ngay': today,
                    'gio_vao': fields.Datetime.now(),
                })
            else:
                cham_cong.write({'gio_vao': fields.Datetime.now()})
        else:  # ra
            if cham_cong:
                cham_cong.write({'gio_ra': fields.Datetime.now()})
        
        return {'success': True}
```

**Lợi ích**:
- ✅ Làm việc mọi lúc mọi nơi
- ✅ Cập nhật real-time
- ✅ Tiện lợi cho nhân viên

---

### 4. TÍCH HỢP BÊN NGOÀI

#### Tính năng:
- Tích hợp Slack/Teams
- Tích hợp Google Calendar
- Tích hợp Jira
- Tích hợp GitLab/GitHub
- Webhook

#### Model mới:
```python
class TichHop(models.Model):
    _name = 'he_thong.tich_hop'
    _description = 'Tích hợp bên ngoài'
    
    ten_tich_hop = fields.Char('Tên', required=True)
    loai = fields.Selection([
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('calendar', 'Google Calendar'),
        ('jira', 'Jira'),
        ('gitlab', 'GitLab'),
        ('github', 'GitHub'),
        ('webhook', 'Webhook')
    ], required=True)
    
    api_key = fields.Char('API Key')
    api_secret = fields.Char('API Secret')
    webhook_url = fields.Char('Webhook URL')
    
    kich_hoat = fields.Boolean('Kích hoạt', default=True)
    
    def gui_thong_bao_slack(self, message):
        """Gửi thông báo lên Slack"""
        if self.loai == 'slack' and self.webhook_url:
            import requests
            requests.post(self.webhook_url, json={'text': message})
    
    def dong_bo_calendar(self, cuoc_hop):
        """Đồng bộ cuộc họp lên Google Calendar"""
        if self.loai == 'calendar':
            # Implement Google Calendar API
            pass
```

**Lợi ích**:
- ✅ Kết nối với công cụ đang dùng
- ✅ Tăng năng suất
- ✅ Tự động hóa workflow

---


## 📊 ROADMAP TRIỂN KHAI

### Phase 1: Nền tảng (Tháng 1-2)
**Module Nhân sự**:
- ✅ Quản lý hợp đồng lao động
- ✅ Quản lý chấm công và nghỉ phép

**Module Dự án**:
- ✅ Quản lý rủi ro
- ✅ Quản lý vấn đề (Issue tracking)

**Ưu tiên**: HIGH - Các tính năng cơ bản, cần thiết nhất

---

### Phase 2: Mở rộng (Tháng 3-4)
**Module Nhân sự**:
- ✅ Đánh giá năng lực và KPI
- ✅ Quản lý đào tạo

**Module Dự án**:
- ✅ Quản lý tài liệu
- ✅ Quản lý cuộc họp
- ✅ Báo cáo tiến độ tự động

**Ưu tiên**: MEDIUM - Tăng cường quản lý

---

### Phase 3: Tối ưu (Tháng 5-6)
**Module Nhân sự**:
- ✅ Quản lý lương thưởng

**Module Dự án**:
- ✅ Gantt Chart
- ✅ Resource Allocation
- ✅ Time Tracking

**Ưu tiên**: MEDIUM - Tối ưu hiệu suất

---

### Phase 4: Tích hợp (Tháng 7-8)
**Tích hợp**:
- ✅ Dashboard tổng hợp
- ✅ Hệ thống thông báo
- ✅ Mobile App (MVP)

**Ưu tiên**: HIGH - Tăng trải nghiệm người dùng

---

### Phase 5: Mở rộng (Tháng 9-12)
**Tích hợp bên ngoài**:
- ✅ Slack/Teams
- ✅ Google Calendar
- ✅ Jira/GitLab

**Nâng cao**:
- ✅ AI/ML cho dự đoán tiến độ
- ✅ Chatbot hỗ trợ
- ✅ Advanced Analytics

**Ưu tiên**: LOW - Tính năng nâng cao

---

## 💰 ƯỚC TÍNH CHI PHÍ

### Nhân lực:
```
Backend Developer (Python/Odoo): 2 người x 8 tháng = 16 người/tháng
Frontend Developer (JS/React): 1 người x 4 tháng = 4 người/tháng
Mobile Developer: 1 người x 3 tháng = 3 người/tháng
UI/UX Designer: 1 người x 2 tháng = 2 người/tháng
QA Tester: 1 người x 6 tháng = 6 người/tháng
Project Manager: 1 người x 8 tháng = 8 người/tháng

Tổng: 39 người/tháng
```

### Hạ tầng:
```
Server (AWS/Azure): $200/tháng x 12 = $2,400
Database: $100/tháng x 12 = $1,200
CDN & Storage: $50/tháng x 12 = $600
Monitoring tools: $50/tháng x 12 = $600

Tổng: $4,800/năm
```

### Công cụ & License:
```
Odoo Enterprise (nếu cần): $30/user/tháng
Development tools: $1,000
Testing tools: $500

Tổng: ~$2,000
```

---

## 📈 LỢI ÍCH KỲ VỌNG

### Tiết kiệm thời gian:
- ⏱️ Giảm 50% thời gian báo cáo
- ⏱️ Giảm 70% thời gian tính lương
- ⏱️ Giảm 40% thời gian quản lý công việc

### Tăng hiệu quả:
- 📊 Tăng 30% năng suất làm việc
- 📊 Giảm 50% công việc trễ hạn
- 📊 Tăng 40% tỷ lệ hoàn thành dự án đúng hạn

### Cải thiện quản lý:
- 👥 Quản lý nhân sự chặt chẽ hơn
- 💼 Theo dõi dự án real-time
- 💰 Kiểm soát ngân sách tốt hơn

---

## 🎯 KPI ĐO LƯỜNG THÀNH CÔNG

### Giai đoạn triển khai:
- ✅ 100% tính năng Phase 1 hoàn thành đúng hạn
- ✅ 0 critical bugs sau 1 tuần go-live
- ✅ 90% user training hoàn thành

### Sau 3 tháng sử dụng:
- ✅ 80% nhân viên sử dụng thường xuyên
- ✅ 50% giảm thời gian báo cáo
- ✅ 90% hài lòng với hệ thống

### Sau 6 tháng sử dụng:
- ✅ 95% nhân viên sử dụng thường xuyên
- ✅ 70% giảm thời gian quản lý
- ✅ 30% tăng năng suất
- ✅ ROI > 150%

---

## 🚀 BƯỚC TIẾP THEO

### 1. Phê duyệt kế hoạch
- [ ] Review roadmap
- [ ] Phê duyệt ngân sách
- [ ] Phân công team

### 2. Chuẩn bị
- [ ] Setup môi trường dev
- [ ] Thiết kế database chi tiết
- [ ] Thiết kế UI/UX mockup

### 3. Triển khai Phase 1
- [ ] Sprint planning
- [ ] Development
- [ ] Testing
- [ ] Deployment

### 4. Training & Go-live
- [ ] Tài liệu hướng dẫn
- [ ] Training cho users
- [ ] Pilot testing
- [ ] Official launch

---

## 📚 TÀI LIỆU THAM KHẢO

### Odoo Documentation:
- [Odoo Development](https://www.odoo.com/documentation/16.0/developer.html)
- [Odoo ORM API](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html)
- [Odoo Views](https://www.odoo.com/documentation/16.0/developer/reference/backend/views.html)

### Best Practices:
- [Odoo Guidelines](https://www.odoo.com/documentation/16.0/contributing/development/coding_guidelines.html)
- [Python PEP 8](https://pep8.org/)
- [Git Flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

### Tools:
- [VS Code Odoo Extension](https://marketplace.visualstudio.com/items?itemName=jigar-patel.OdooSnippets)
- [Odoo Debug Mode](https://www.odoo.com/documentation/16.0/applications/general/developer_mode.html)
- [PostgreSQL](https://www.postgresql.org/docs/)

---

## 💡 GỢI Ý BỔ SUNG

### 1. Gamification
Thêm yếu tố game hóa để tăng động lực:
- 🏆 Huy hiệu (Badges) cho thành tích
- 🎯 Bảng xếp hạng (Leaderboard)
- ⭐ Điểm thưởng (Points)
- 🎁 Phần thưởng (Rewards)

### 2. AI/ML Features
Ứng dụng AI để tối ưu:
- 🤖 Dự đoán tiến độ dự án
- 🤖 Gợi ý phân công công việc
- 🤖 Phát hiện rủi ro sớm
- 🤖 Chatbot hỗ trợ

### 3. Advanced Analytics
Phân tích nâng cao:
- 📊 Predictive analytics
- 📊 Trend analysis
- 📊 Performance benchmarking
- 📊 Custom reports

### 4. Collaboration Tools
Công cụ cộng tác:
- 💬 Chat tích hợp
- 📹 Video call
- 📝 Collaborative editing
- 🗂️ File sharing

---

## ✅ CHECKLIST TRIỂN KHAI

### Trước khi bắt đầu:
- [ ] Đánh giá yêu cầu chi tiết
- [ ] Phân tích gap với hệ thống hiện tại
- [ ] Xác định stakeholders
- [ ] Lập kế hoạch chi tiết
- [ ] Phê duyệt ngân sách

### Trong quá trình phát triển:
- [ ] Daily standup meetings
- [ ] Code review
- [ ] Unit testing
- [ ] Integration testing
- [ ] Documentation

### Trước khi go-live:
- [ ] UAT (User Acceptance Testing)
- [ ] Performance testing
- [ ] Security audit
- [ ] Backup & recovery plan
- [ ] Training materials

### Sau go-live:
- [ ] Monitor system performance
- [ ] Collect user feedback
- [ ] Bug fixing
- [ ] Continuous improvement
- [ ] Regular updates

---

## 🎓 KẾT LUẬN

Hệ thống 3 modules (Nhân sự - Dự án - Công việc) có tiềm năng phát triển rất lớn. Với roadmap rõ ràng và các tính năng được ưu tiên hợp lý, hệ thống sẽ:

✅ **Tăng hiệu quả quản lý** lên 40-50%
✅ **Giảm thời gian** xử lý công việc 30-40%
✅ **Cải thiện trải nghiệm** người dùng
✅ **Tạo nền tảng** cho digital transformation

**Khuyến nghị**: Bắt đầu với Phase 1 (Hợp đồng + Chấm công + Rủi ro + Issue tracking) để có kết quả nhanh và tạo động lực cho team.

---

**Tài liệu này được tạo bởi Kiro AI**
*Cập nhật lần cuối: 2026-01-28*
*Phiên bản: 2.0*

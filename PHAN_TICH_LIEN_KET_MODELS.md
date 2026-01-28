# 🔗 PHÂN TÍCH LIÊN KẾT GIỮA CÁC MODELS

## 📋 MỤC LỤC
1. [Tổng quan hệ thống](#tong-quan)
2. [Module Nhân sự](#module-nhan-su)
3. [Module Quản lý công việc](#module-quan-ly-cong-viec)
4. [Module Quản lý dự án](#module-quan-ly-du-an)
5. [Liên kết giữa các modules](#lien-ket-cross-module)
6. [Sơ đồ tổng hợp](#so-do-tong-hop)
7. [Luồng dữ liệu](#luong-du-lieu)
8. [Best Practices](#best-practices)

---

## 🎯 TỔNG QUAN HỆ THỐNG {#tong-quan}

### Kiến trúc 3 tầng:
```
┌─────────────────────────────────────────────────────────┐
│                    HỆ THỐNG QUẢN LÝ                     │
├─────────────────────────────────────────────────────────┤
│  Module 1: NHÂN SỰ (nhan_su)                           │
│  - Quản lý nhân viên, đơn vị, chức vụ                  │
│  - Lịch sử công tác, chứng chỉ                         │
│  - Cung cấp thông tin nhân sự cho các module khác      │
├─────────────────────────────────────────────────────────┤
│  Module 2: QUẢN LÝ DỰ ÁN (quan_ly_du_an)              │
│  - Quản lý dự án, giai đoạn                            │
│  - Phân bổ nhân sự, tài chính                          │
│  - Liên kết với nhân sự và công việc                   │
├─────────────────────────────────────────────────────────┤
│  Module 3: QUẢN LÝ CÔNG VIỆC (quan_ly_cong_viec)      │
│  - Quản lý công việc, task                             │
│  - Giai đoạn công việc, tài nguyên                     │
│  - Phụ thuộc vào dự án và nhân sự                      │
└─────────────────────────────────────────────────────────┘
```

### Thứ tự phụ thuộc:
```
nhan_su (độc lập)
    ↓
quan_ly_du_an (phụ thuộc nhan_su)
    ↓
quan_ly_cong_viec (phụ thuộc nhan_su + quan_ly_du_an)
```

---

## 👥 MODULE NHÂN SỰ (nhan_su) {#module-nhan-su}

### Sơ đồ quan hệ:
```

┌──────────────────┐
│   don_vi         │ ◄──────┐
│  (Đơn vị)        │        │ Many2one
└──────────────────┘        │
                            │
┌──────────────────┐        │
│   chuc_vu        │ ◄──────┤
│  (Chức vụ)       │        │
└──────────────────┘        │
                            │
┌──────────────────┐        │
│   nhan_vien      │ ───────┤
│  (Nhân viên)     │        │
│  [MODEL TRUNG TÂM]│       │
└──────────────────┘        │
        │                   │
        │ One2many          │
        ├───────────────────┘
        │
        ├──► lich_su_cong_tac (Lịch sử công tác)
        │
        ├──► chung_chi_bang_cap (Chứng chỉ)
        │
        └──► ky_nang (Kỹ năng)
```

### Chi tiết các models:

#### 1. nhan_su.nhan_vien (Model trung tâm)
**Vai trò**: Model cốt lõi, được tham chiếu bởi tất cả các module khác

**Quan hệ Many2one** (Thuộc về):
- `don_vi_id` → `nhan_su.don_vi`: Nhân viên thuộc đơn vị nào
- `chuc_vu_id` → `nhan_su.chuc_vu`: Nhân viên giữ chức vụ gì

**Quan hệ One2many** (Có nhiều):
- `lich_su_cong_tac_ids` ← `nhan_su.lich_su_cong_tac`: Lịch sử làm việc
- `chung_chi_ids` ← `nhan_su.chung_chi_bang_cap`: Các chứng chỉ
- `ky_nang_ids` ← `nhan_su.ky_nang`: Các kỹ năng

**Computed Fields**:
```python
# Tính tuổi từ ngày sinh
tuoi = fields.Integer(compute='_compute_tuoi')

# Tính thâm niên từ ngày vào làm
tham_nien = fields.Float(compute='_compute_tham_nien')

# Tên đầy đủ = Họ + Tên
ho_va_ten = fields.Char(compute='_compute_ho_va_ten', store=True)
```

**Ví dụ sử dụng**:
```python
# Tạo nhân viên mới
nhan_vien = env['nhan_su.nhan_vien'].create({
    'ho': 'Nguyễn',
    'ten': 'Văn A',
    'ngay_sinh': '1990-01-01',
    'don_vi_id': don_vi_id,
    'chuc_vu_id': chuc_vu_id,
})

# Truy cập thông tin
print(nhan_vien.ho_va_ten)  # "Nguyễn Văn A"
print(nhan_vien.tuoi)  # 36
print(nhan_vien.don_vi_id.ten_don_vi)  # "Phòng IT"
```

---

#### 2. nhan_su.don_vi
**Vai trò**: Cấu trúc tổ chức công ty

**Quan hệ One2many**:
- `nhan_vien_ids` ← `nhan_su.nhan_vien`: Danh sách nhân viên trong đơn vị

**Computed Fields**:
```python
# Đếm số nhân viên
so_nhan_vien = fields.Integer(compute='_compute_so_nhan_vien')
```

**Ví dụ**:
```python
# Lấy tất cả nhân viên của phòng IT
phong_it = env['nhan_su.don_vi'].search([('ten_don_vi', '=', 'Phòng IT')])
for nv in phong_it.nhan_vien_ids:
    print(nv.ho_va_ten)
```

---

#### 3. nhan_su.chuc_vu
**Vai trò**: Vị trí công việc trong tổ chức

**Quan hệ One2many**:
- `nhan_vien_ids` ← `nhan_su.nhan_vien`: Nhân viên giữ chức vụ này

**Computed Fields**:
```python
so_nhan_vien = fields.Integer(compute='_compute_so_nhan_vien')
```

---

#### 4. nhan_su.lich_su_cong_tac
**Vai trò**: Theo dõi quá trình làm việc

**Quan hệ Many2one**:
- `nhan_vien_id` → `nhan_su.nhan_vien`: Lịch sử của nhân viên nào
- `don_vi_id` → `nhan_su.don_vi`: Làm việc tại đơn vị nào
- `chuc_vu_id` → `nhan_su.chuc_vu`: Giữ chức vụ gì

**Ví dụ**:
```python
# Tạo lịch sử thăng chức
env['nhan_su.lich_su_cong_tac'].create({
    'nhan_vien_id': nhan_vien.id,
    'loai_thay_doi': 'thang_chuc',
    'chuc_vu_id': chuc_vu_moi.id,
    'ngay_hieu_luc': '2026-01-01',
    'ghi_chu': 'Thăng chức lên Trưởng phòng'
})
```

---


## 📊 MODULE QUẢN LÝ DỰ ÁN (quan_ly_du_an) {#module-quan-ly-du-an}

### Sơ đồ quan hệ:
```
┌──────────────────────┐
│   du_an              │
│   (Dự án)            │
│   [MODEL TRUNG TÂM]  │
└──────────────────────┘
        │
        │ One2many
        ├──► giai_doan_du_an (Giai đoạn)
        │
        ├──► nhan_su_du_an (Nhân sự tham gia)
        │         │
        │         └──► Many2one → nhan_su.nhan_vien
        │
        └──► tai_chinh_du_an (Tài chính)
```

### Chi tiết các models:

#### 1. quan_ly_du_an.du_an (Model trung tâm)
**Vai trò**: Quản lý thông tin dự án, là trung tâm liên kết với công việc

**Quan hệ Many2one**:
- `quan_ly_du_an_id` → `nhan_su.nhan_vien`: Người quản lý dự án
- `khach_hang_id` → `res.partner`: Khách hàng (model chuẩn Odoo)

**Quan hệ One2many**:
- `giai_doan_ids` ← `quan_ly_du_an.giai_doan_du_an`: Các giai đoạn
- `nhan_su_ids` ← `quan_ly_du_an.nhan_su_du_an`: Nhân sự tham gia
- `tai_chinh_ids` ← `quan_ly_du_an.tai_chinh_du_an`: Thông tin tài chính

**Computed Fields**:
```python
# Tính tiến độ từ giai đoạn
tien_do = fields.Float(compute='_compute_tien_do')

# Tổng ngân sách từ tài chính
tong_ngan_sach = fields.Float(compute='_compute_tong_ngan_sach')

# Số nhân sự tham gia
so_nhan_su = fields.Integer(compute='_compute_so_nhan_su')
```

**Ví dụ sử dụng**:
```python
# Tạo dự án mới
du_an = env['quan_ly_du_an.du_an'].create({
    'ten_du_an': 'Xây dựng hệ thống ERP',
    'ma_du_an': 'DA001',
    'ngay_bat_dau': '2026-01-01',
    'ngay_ket_thuc': '2026-12-31',
    'quan_ly_du_an_id': quan_ly_id,
    'trang_thai': 'dang_thuc_hien',
})

# Thêm nhân sự vào dự án
env['quan_ly_du_an.nhan_su_du_an'].create({
    'du_an_id': du_an.id,
    'nhan_vien_id': nhan_vien.id,
    'vai_tro': 'developer',
    'ngay_tham_gia': '2026-01-15',
})
```

---

#### 2. quan_ly_du_an.giai_doan_du_an
**Vai trò**: Chia dự án thành các giai đoạn nhỏ

**Quan hệ Many2one**:
- `du_an_id` → `quan_ly_du_an.du_an`: Thuộc dự án nào

**Computed Fields**:
```python
# Tính tiến độ giai đoạn
tien_do = fields.Float(compute='_compute_tien_do')
```

**Ví dụ**:
```python
# Tạo giai đoạn phân tích
env['quan_ly_du_an.giai_doan_du_an'].create({
    'du_an_id': du_an.id,
    'ten_giai_doan': 'Phân tích yêu cầu',
    'ngay_bat_dau': '2026-01-01',
    'ngay_ket_thuc': '2026-02-01',
    'tien_do': 0,
})
```

---

#### 3. quan_ly_du_an.nhan_su_du_an
**Vai trò**: Liên kết nhân viên với dự án (Many2many relationship table)

**Quan hệ Many2one**:
- `du_an_id` → `quan_ly_du_an.du_an`: Dự án nào
- `nhan_vien_id` → `nhan_su.nhan_vien`: Nhân viên nào

**Trường đặc biệt**:
- `vai_tro`: Vai trò trong dự án (PM, Dev, Tester...)
- `ngay_tham_gia`, `ngay_roi_khoi`: Thời gian tham gia

**Ví dụ truy vấn**:
```python
# Lấy tất cả dự án của một nhân viên
nhan_su_du_an = env['quan_ly_du_an.nhan_su_du_an'].search([
    ('nhan_vien_id', '=', nhan_vien.id)
])
for ns in nhan_su_du_an:
    print(f"{ns.du_an_id.ten_du_an} - {ns.vai_tro}")

# Lấy tất cả nhân viên của một dự án
for ns in du_an.nhan_su_ids:
    print(f"{ns.nhan_vien_id.ho_va_ten} - {ns.vai_tro}")
```

---

#### 4. quan_ly_du_an.tai_chinh_du_an
**Vai trò**: Quản lý ngân sách và chi phí

**Quan hệ Many2one**:
- `du_an_id` → `quan_ly_du_an.du_an`: Thuộc dự án nào

**Ví dụ**:
```python
# Thêm khoản chi
env['quan_ly_du_an.tai_chinh_du_an'].create({
    'du_an_id': du_an.id,
    'loai': 'chi',
    'so_tien': 50000000,
    'mo_ta': 'Chi phí nhân công tháng 1',
    'ngay_ghi_nhan': '2026-01-31',
})
```

---


## ⚙️ MODULE QUẢN LÝ CÔNG VIỆC (quan_ly_cong_viec) {#module-quan-ly-cong-viec}

### Sơ đồ quan hệ:
```
┌──────────────────────┐
│   cong_viec          │
│   (Công việc)        │
│   [MODEL TRUNG TÂM]  │
└──────────────────────┘
        │
        │ Many2one
        ├──► quan_ly_du_an.du_an (Thuộc dự án)
        │
        ├──► nhan_su.nhan_vien (Người thực hiện)
        │
        ├──► nhan_su.nhan_vien (Người giao việc)
        │
        │ One2many
        ├──► nhat_ky_cong_viec (Nhật ký)
        │
        ├──► tai_nguyen (Tài nguyên)
        │
        └──► giai_doan_cong_viec (Giai đoạn)
```

### Chi tiết các models:

#### 1. quan_ly_cong_viec.cong_viec (Model trung tâm)
**Vai trò**: Quản lý công việc cụ thể trong dự án

**Quan hệ Many2one** (Liên kết với module khác):
- `du_an_id` → `quan_ly_du_an.du_an`: Công việc thuộc dự án nào
- `nguoi_thuc_hien_id` → `nhan_su.nhan_vien`: Ai làm
- `nguoi_giao_viec_id` → `nhan_su.nhan_vien`: Ai giao

**Quan hệ One2many**:
- `nhat_ky_ids` ← `quan_ly_cong_viec.nhat_ky_cong_viec`: Nhật ký cập nhật
- `tai_nguyen_ids` ← `quan_ly_cong_viec.tai_nguyen`: Tài nguyên cần thiết
- `giai_doan_ids` ← `quan_ly_cong_viec.giai_doan_cong_viec`: Các giai đoạn

**Computed Fields**:
```python
# Tính tiến độ
tien_do = fields.Float(compute='_compute_tien_do')

# Số giờ đã làm
so_gio_da_lam = fields.Float(compute='_compute_so_gio')

# Trạng thái trễ hạn
tre_han = fields.Boolean(compute='_compute_tre_han')
```

**Ví dụ sử dụng**:
```python
# Tạo công việc mới
cong_viec = env['quan_ly_cong_viec.cong_viec'].create({
    'ten_cong_viec': 'Thiết kế database',
    'du_an_id': du_an.id,
    'nguoi_thuc_hien_id': nhan_vien.id,
    'nguoi_giao_viec_id': quan_ly.id,
    'ngay_bat_dau': '2026-01-15',
    'ngay_ket_thuc': '2026-01-30',
    'uu_tien': 'cao',
    'trang_thai': 'dang_thuc_hien',
})

# Cập nhật tiến độ
cong_viec.write({'tien_do': 50})

# Thêm nhật ký
env['quan_ly_cong_viec.nhat_ky_cong_viec'].create({
    'cong_viec_id': cong_viec.id,
    'noi_dung': 'Đã hoàn thành 5/10 bảng',
    'tien_do': 50,
})
```

---

#### 2. quan_ly_cong_viec.nhat_ky_cong_viec
**Vai trò**: Ghi lại quá trình thực hiện công việc

**Quan hệ Many2one**:
- `cong_viec_id` → `quan_ly_cong_viec.cong_viec`: Nhật ký của công việc nào
- `du_an_id` → `quan_ly_du_an.du_an`: Thuộc dự án nào (để báo cáo)
- `nguoi_cap_nhat_id` → `nhan_su.nhan_vien`: Ai cập nhật

**Ví dụ**:
```python
# Xem lịch sử công việc
for nhat_ky in cong_viec.nhat_ky_ids:
    print(f"{nhat_ky.ngay_cap_nhat}: {nhat_ky.noi_dung} - {nhat_ky.tien_do}%")
```

---

#### 3. quan_ly_cong_viec.tai_nguyen
**Vai trò**: Quản lý tài nguyên cần cho công việc

**Quan hệ Many2one**:
- `cong_viec_id` → `quan_ly_cong_viec.cong_viec`: Tài nguyên cho công việc nào
- `du_an_id` → `quan_ly_du_an.du_an`: Thuộc dự án nào

**Ví dụ**:
```python
# Thêm tài nguyên
env['quan_ly_cong_viec.tai_nguyen'].create({
    'cong_viec_id': cong_viec.id,
    'du_an_id': du_an.id,
    'ten_tai_nguyen': 'Server AWS',
    'loai_tai_nguyen': 'thiet_bi',
    'so_luong': 1,
    'don_vi_tinh': 'cái',
})
```

---

#### 4. quan_ly_cong_viec.giai_doan_cong_viec
**Vai trò**: Chia công việc thành các giai đoạn nhỏ

**Quan hệ Many2one**:
- `cong_viec_id` → `quan_ly_cong_viec.cong_viec`: Giai đoạn của công việc nào
- `du_an_id` → `quan_ly_du_an.du_an`: Thuộc dự án nào

---

#### 5. quan_ly_cong_viec.danh_gia_nhan_vien
**Vai trò**: Đánh giá hiệu suất làm việc

**Quan hệ Many2one**:
- `nhan_vien_id` → `nhan_su.nhan_vien`: Đánh giá nhân viên nào
- `du_an_id` → `quan_ly_du_an.du_an`: Trong dự án nào
- `nguoi_danh_gia_id` → `nhan_su.nhan_vien`: Ai đánh giá

**Ví dụ**:
```python
# Đánh giá nhân viên
env['quan_ly_cong_viec.danh_gia_nhan_vien'].create({
    'nhan_vien_id': nhan_vien.id,
    'du_an_id': du_an.id,
    'nguoi_danh_gia_id': quan_ly.id,
    'diem_so': 8.5,
    'nhan_xet': 'Làm việc tốt, đúng deadline',
})
```

---

#### 6. quan_ly_cong_viec.dashboard
**Vai trò**: Tổng hợp thống kê

**Quan hệ Many2one**:
- `du_an_id` → `quan_ly_du_an.du_an`: Dashboard của dự án nào

**Computed Fields** (Tất cả đều computed):
```python
tong_cong_viec = fields.Integer(compute='_compute_thong_ke')
cong_viec_hoan_thanh = fields.Integer(compute='_compute_thong_ke')
cong_viec_dang_lam = fields.Integer(compute='_compute_thong_ke')
cong_viec_tre_han = fields.Integer(compute='_compute_thong_ke')
```

---


## 🔗 LIÊN KẾT GIỮA CÁC MODULES {#lien-ket-cross-module}

### 1. Nhân sự → Dự án
```python
# Model: quan_ly_du_an.du_an
quan_ly_du_an_id = fields.Many2one('nhan_su.nhan_vien')

# Model: quan_ly_du_an.nhan_su_du_an
nhan_vien_id = fields.Many2one('nhan_su.nhan_vien')
```

**Ý nghĩa**: 
- Dự án cần có người quản lý (từ module nhân sự)
- Dự án có nhiều nhân viên tham gia (từ module nhân sự)

**Ví dụ truy vấn**:
```python
# Lấy tất cả dự án mà nhân viên tham gia
nhan_su_du_an = env['quan_ly_du_an.nhan_su_du_an'].search([
    ('nhan_vien_id', '=', nhan_vien.id)
])
du_an_ids = nhan_su_du_an.mapped('du_an_id')

# Lấy tất cả dự án do nhân viên quản lý
du_an_quan_ly = env['quan_ly_du_an.du_an'].search([
    ('quan_ly_du_an_id', '=', nhan_vien.id)
])
```

---

### 2. Nhân sự → Công việc
```python
# Model: quan_ly_cong_viec.cong_viec
nguoi_thuc_hien_id = fields.Many2one('nhan_su.nhan_vien')
nguoi_giao_viec_id = fields.Many2one('nhan_su.nhan_vien')

# Model: quan_ly_cong_viec.nhat_ky_cong_viec
nguoi_cap_nhat_id = fields.Many2one('nhan_su.nhan_vien')

# Model: quan_ly_cong_viec.danh_gia_nhan_vien
nhan_vien_id = fields.Many2one('nhan_su.nhan_vien')
nguoi_danh_gia_id = fields.Many2one('nhan_su.nhan_vien')
```

**Ý nghĩa**:
- Công việc được giao cho nhân viên cụ thể
- Công việc được giao bởi người quản lý
- Nhật ký được cập nhật bởi nhân viên
- Đánh giá liên kết với nhân viên

---

### 3. Dự án → Công việc
```python
# Model: quan_ly_cong_viec.cong_viec
du_an_id = fields.Many2one('quan_ly_du_an.du_an')

# Model: quan_ly_cong_viec.nhat_ky_cong_viec
du_an_id = fields.Many2one('quan_ly_du_an.du_an')

# Model: quan_ly_cong_viec.tai_nguyen
du_an_id = fields.Many2one('quan_ly_du_an.du_an')

# Model: quan_ly_cong_viec.giai_doan_cong_viec
du_an_id = fields.Many2one('quan_ly_du_an.du_an')

# Model: quan_ly_cong_viec.danh_gia_nhan_vien
du_an_id = fields.Many2one('quan_ly_du_an.du_an')

# Model: quan_ly_cong_viec.dashboard
du_an_id = fields.Many2one('quan_ly_du_an.du_an')
```

**Ý nghĩa**:
- Tất cả công việc đều thuộc về một dự án
- Mọi hoạt động trong module công việc đều liên kết với dự án

---

### 4. Sơ đồ liên kết tổng hợp:
```
┌─────────────────────────────────────────────────────────────┐
│                    MODULE NHÂN SỰ                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  nhan_vien   │  │   don_vi     │  │   chuc_vu    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ Many2one           │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                  MODULE QUẢN LÝ DỰ ÁN                       │
│  ┌──────────────────────────────────────────────────┐      │
│  │  du_an                                           │      │
│  │  - quan_ly_du_an_id → nhan_su.nhan_vien        │      │
│  └──────────────────────────────────────────────────┘      │
│         │                                                    │
│         ├──► giai_doan_du_an                               │
│         ├──► nhan_su_du_an → nhan_su.nhan_vien            │
│         └──► tai_chinh_du_an                               │
└─────────────────────────────────────────────────────────────┘
         │
         │ Many2one
         ▼
┌─────────────────────────────────────────────────────────────┐
│                MODULE QUẢN LÝ CÔNG VIỆC                     │
│  ┌──────────────────────────────────────────────────┐      │
│  │  cong_viec                                       │      │
│  │  - du_an_id → quan_ly_du_an.du_an              │      │
│  │  - nguoi_thuc_hien_id → nhan_su.nhan_vien     │      │
│  │  - nguoi_giao_viec_id → nhan_su.nhan_vien     │      │
│  └──────────────────────────────────────────────────┘      │
│         │                                                    │
│         ├──► nhat_ky_cong_viec                             │
│         ├──► tai_nguyen                                     │
│         ├──► giai_doan_cong_viec                           │
│         ├──► danh_gia_nhan_vien                            │
│         └──► dashboard                                      │
└─────────────────────────────────────────────────────────────┘
```

---


## 📊 SƠ ĐỒ TỔNG HỢP {#so-do-tong-hop}

### Sơ đồ ER (Entity Relationship):
```
                    ┌─────────────────┐
                    │   res.partner   │
                    │   (Khách hàng)  │
                    └─────────────────┘
                            │
                            │ Many2one
                            ▼
    ┌──────────────┐   ┌─────────────────┐   ┌──────────────┐
    │   don_vi     │◄──│  nhan_vien      │──►│   chuc_vu    │
    │              │   │  [CORE MODEL]   │   │              │
    └──────────────┘   └─────────────────┘   └──────────────┘
                            │       │
                            │       └──────────┐
                            │                  │
                            ▼                  ▼
                    ┌─────────────────┐   ┌─────────────────┐
                    │ lich_su_cong_tac│   │ chung_chi_bang_cap│
                    └─────────────────┘   └─────────────────┘
                            │
                            │ Many2one
                            ▼
                    ┌─────────────────────────┐
                    │      du_an              │
                    │   [CORE MODEL]          │
                    │ - quan_ly_du_an_id      │
                    │ - khach_hang_id         │
                    └─────────────────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │giai_doan_du_an│ │nhan_su_du_an │ │tai_chinh_du_an│
    │              │ │              │ │              │
    └──────────────┘ └──────────────┘ └──────────────┘
                            │
                            │ Many2one
                            ▼
                    ┌─────────────────────────┐
                    │     cong_viec           │
                    │   [CORE MODEL]          │
                    │ - du_an_id              │
                    │ - nguoi_thuc_hien_id    │
                    │ - nguoi_giao_viec_id    │
                    └─────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│nhat_ky_cong_viec│ │  tai_nguyen  │   │giai_doan_cv  │
└──────────────┘   └──────────────┘   └──────────────┘
        │
        ▼
┌──────────────┐
│danh_gia_nv   │
└──────────────┘
```

### Ma trận quan hệ:
```
┌────────────────┬─────────┬─────────┬─────────┬─────────┐
│                │ nhan_su │ du_an   │cong_viec│ partner │
├────────────────┼─────────┼─────────┼─────────┼─────────┤
│ nhan_vien      │    -    │   M2O   │   M2O   │    -    │
│ don_vi         │   O2M   │    -    │    -    │    -    │
│ chuc_vu        │   O2M   │    -    │    -    │    -    │
│ du_an          │   M2O   │    -    │   O2M   │   M2O   │
│ nhan_su_du_an  │   M2O   │   M2O   │    -    │    -    │
│ cong_viec      │   M2O   │   M2O   │    -    │    -    │
│ nhat_ky        │   M2O   │   M2O   │   M2O   │    -    │
│ tai_nguyen     │    -    │   M2O   │   M2O   │    -    │
│ danh_gia       │   M2O   │   M2O   │    -    │    -    │
└────────────────┴─────────┴─────────┴─────────┴─────────┘

Chú thích:
- M2O: Many2one (Nhiều-Một)
- O2M: One2many (Một-Nhiều)
- M2M: Many2many (Nhiều-Nhiều)
```

---

## 🔄 LUỒNG DỮ LIỆU {#luong-du-lieu}

### 1. Luồng tạo dự án mới:
```
Bước 1: Tạo nhân viên (nếu chưa có)
    ↓
Bước 2: Tạo dự án
    - Chọn người quản lý (nhan_su.nhan_vien)
    - Chọn khách hàng (res.partner)
    ↓
Bước 3: Thêm nhân sự vào dự án
    - Tạo bản ghi nhan_su_du_an
    - Liên kết nhan_vien với du_an
    ↓
Bước 4: Tạo giai đoạn dự án
    - Tạo giai_doan_du_an
    ↓
Bước 5: Tạo công việc
    - Liên kết với du_an
    - Gán cho nhan_vien
```

**Code minh họa**:
```python
# Bước 1: Tạo nhân viên
nhan_vien = env['nhan_su.nhan_vien'].create({
    'ho': 'Nguyễn',
    'ten': 'Văn A',
    'don_vi_id': don_vi_id,
    'chuc_vu_id': chuc_vu_id,
})

# Bước 2: Tạo dự án
du_an = env['quan_ly_du_an.du_an'].create({
    'ten_du_an': 'Dự án ERP',
    'quan_ly_du_an_id': quan_ly_id,
    'khach_hang_id': khach_hang_id,
})

# Bước 3: Thêm nhân sự
env['quan_ly_du_an.nhan_su_du_an'].create({
    'du_an_id': du_an.id,
    'nhan_vien_id': nhan_vien.id,
    'vai_tro': 'developer',
})

# Bước 4: Tạo giai đoạn
giai_doan = env['quan_ly_du_an.giai_doan_du_an'].create({
    'du_an_id': du_an.id,
    'ten_giai_doan': 'Phân tích',
})

# Bước 5: Tạo công việc
cong_viec = env['quan_ly_cong_viec.cong_viec'].create({
    'ten_cong_viec': 'Thiết kế database',
    'du_an_id': du_an.id,
    'nguoi_thuc_hien_id': nhan_vien.id,
})
```

---

### 2. Luồng cập nhật tiến độ:
```
Nhân viên cập nhật công việc
    ↓
Tạo nhat_ky_cong_viec
    - Ghi lại tiến độ
    - Ghi lại nội dung
    ↓
Cập nhật tien_do của cong_viec
    ↓
Tự động tính tien_do của du_an
    - Dựa trên tất cả công việc
    ↓
Dashboard tự động cập nhật
    - Thống kê real-time
```

**Code minh họa**:
```python
# Cập nhật tiến độ công việc
cong_viec.write({'tien_do': 50})

# Tạo nhật ký
env['quan_ly_cong_viec.nhat_ky_cong_viec'].create({
    'cong_viec_id': cong_viec.id,
    'du_an_id': du_an.id,
    'nguoi_cap_nhat_id': nhan_vien.id,
    'noi_dung': 'Đã hoàn thành 50%',
    'tien_do': 50,
})

# Tiến độ dự án tự động tính
print(du_an.tien_do)  # Computed từ tất cả công việc
```

---

### 3. Luồng báo cáo:
```
Dashboard query dữ liệu
    ↓
Lấy thông tin từ cong_viec
    - Tổng số công việc
    - Công việc hoàn thành
    - Công việc trễ hạn
    ↓
Lấy thông tin từ du_an
    - Tiến độ dự án
    - Ngân sách
    ↓
Lấy thông tin từ nhan_vien
    - Số nhân sự
    - Hiệu suất
    ↓
Hiển thị dashboard
```

---


## 💡 BEST PRACTICES {#best-practices}

### 1. Sử dụng namespace đúng cách:
```python
# ✅ ĐÚNG: Sử dụng namespace đầy đủ
du_an_id = fields.Many2one('quan_ly_du_an.du_an')
nhan_vien_id = fields.Many2one('nhan_su.nhan_vien')

# ❌ SAI: Không dùng namespace
du_an_id = fields.Many2one('du_an')  # Sẽ bị lỗi!
```

---

### 2. Sử dụng ondelete đúng:
```python
# Khi xóa dự án → xóa tất cả công việc
du_an_id = fields.Many2one('quan_ly_du_an.du_an', ondelete='cascade')

# Khi xóa nhân viên → giữ lại công việc, set NULL
nguoi_thuc_hien_id = fields.Many2one('nhan_su.nhan_vien', ondelete='set null')

# Khi xóa nhân viên → không cho xóa nếu còn dự án
quan_ly_du_an_id = fields.Many2one('nhan_su.nhan_vien', ondelete='restrict')
```

---

### 3. Sử dụng inverse_name cho One2many:
```python
# Model: du_an
nhan_su_ids = fields.One2many('quan_ly_du_an.nhan_su_du_an', 'du_an_id')

# Model: nhan_su_du_an
du_an_id = fields.Many2one('quan_ly_du_an.du_an')  # inverse_name
```

---

### 4. Truy vấn cross-module hiệu quả:
```python
# ❌ SAI: Query nhiều lần
for cong_viec in cong_viec_ids:
    print(cong_viec.du_an_id.ten_du_an)  # N+1 query problem

# ✅ ĐÚNG: Sử dụng mapped()
du_an_ids = cong_viec_ids.mapped('du_an_id')
print(du_an_ids.mapped('ten_du_an'))

# ✅ ĐÚNG: Sử dụng search với domain
cong_viec_ids = env['quan_ly_cong_viec.cong_viec'].search([
    ('du_an_id.trang_thai', '=', 'dang_thuc_hien'),
    ('nguoi_thuc_hien_id.don_vi_id.ten_don_vi', '=', 'Phòng IT')
])
```

---

### 5. Sử dụng computed fields với store:
```python
# Computed field với store=True để tăng performance
tien_do = fields.Float(compute='_compute_tien_do', store=True)

@api.depends('cong_viec_ids.tien_do')
def _compute_tien_do(self):
    for record in self:
        if record.cong_viec_ids:
            record.tien_do = sum(record.cong_viec_ids.mapped('tien_do')) / len(record.cong_viec_ids)
```

---

### 6. Sử dụng related fields:
```python
# Thay vì viết computed field phức tạp
# ✅ ĐÚNG: Sử dụng related
class CongViec(models.Model):
    du_an_id = fields.Many2one('quan_ly_du_an.du_an')
    quan_ly_du_an_id = fields.Many2one(
        related='du_an_id.quan_ly_du_an_id',
        string='Quản lý dự án',
        store=True
    )
```

---

### 7. Ví dụ truy vấn phức tạp:
```python
# Lấy tất cả công việc của nhân viên trong tháng này
from datetime import datetime, timedelta

start_date = datetime.now().replace(day=1)
end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

cong_viec_ids = env['quan_ly_cong_viec.cong_viec'].search([
    ('nguoi_thuc_hien_id', '=', nhan_vien.id),
    ('ngay_bat_dau', '>=', start_date),
    ('ngay_bat_dau', '<=', end_date),
])

# Thống kê theo dự án
for du_an in cong_viec_ids.mapped('du_an_id'):
    cv_cua_du_an = cong_viec_ids.filtered(lambda x: x.du_an_id == du_an)
    print(f"{du_an.ten_du_an}: {len(cv_cua_du_an)} công việc")
```

---

### 8. Sử dụng domain trong view:
```xml
<!-- Chỉ hiển thị nhân viên của phòng IT -->
<field name="nguoi_thuc_hien_id" 
       domain="[('don_vi_id.ten_don_vi', '=', 'Phòng IT')]"/>

<!-- Chỉ hiển thị dự án đang thực hiện -->
<field name="du_an_id" 
       domain="[('trang_thai', '=', 'dang_thuc_hien')]"/>

<!-- Domain động dựa trên field khác -->
<field name="du_an_id"/>
<field name="nguoi_thuc_hien_id" 
       domain="[('id', 'in', du_an_id.nhan_su_ids.mapped('nhan_vien_id').ids)]"/>
```

---

### 9. Sử dụng context:
```python
# Truyền context khi tạo record
cong_viec = env['quan_ly_cong_viec.cong_viec'].with_context(
    default_du_an_id=du_an.id,
    default_nguoi_giao_viec_id=env.user.employee_id.id
).create({
    'ten_cong_viec': 'Task mới',
})
```

---

### 10. Xử lý lỗi khi liên kết:
```python
# Kiểm tra tồn tại trước khi truy cập
if cong_viec.du_an_id:
    print(cong_viec.du_an_id.ten_du_an)
else:
    print("Công việc chưa được gán dự án")

# Sử dụng exists() để lọc record đã bị xóa
du_an_ids = cong_viec_ids.mapped('du_an_id').exists()
```

---

## 📈 THỐNG KÊ HỆ THỐNG

### Tổng số models: 17
- Module nhân sự: 5 models
- Module dự án: 4 models
- Module công việc: 8 models

### Tổng số quan hệ Many2one: 28
- Nhân sự → Nhân sự: 2
- Nhân sự → Dự án: 3
- Nhân sự → Công việc: 6
- Dự án → Công việc: 6
- Nội bộ module: 11

### Tổng số quan hệ One2many: 15
- Module nhân sự: 3
- Module dự án: 3
- Module công việc: 9

---

## 🎓 KẾT LUẬN

Hệ thống 3 modules được thiết kế với kiến trúc phân tầng rõ ràng:

1. **Module Nhân sự** là nền tảng, cung cấp thông tin nhân viên cho toàn hệ thống
2. **Module Dự án** là trung gian, liên kết nhân sự với công việc cụ thể
3. **Module Công việc** là tầng cao nhất, quản lý chi tiết các task

Các liên kết được thiết kế:
- ✅ Rõ ràng, dễ hiểu
- ✅ Tránh circular dependency
- ✅ Tối ưu performance với store=True
- ✅ Linh hoạt với computed fields
- ✅ An toàn với ondelete constraints

---

**Tài liệu này được tạo tự động bởi Kiro AI**
*Cập nhật lần cuối: 2026-01-28*

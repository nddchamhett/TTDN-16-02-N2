# 🛑 HƯỚNG DẪN TÍNH NĂNG TẠM DỪNG DỰ ÁN

## 📋 TỔNG QUAN

Tính năng "Tạm dừng dự án" cho phép tạm ngưng một dự án đang thực hiện mà không ảnh hưởng đến logic tự động cập nhật trạng thái.

---

## 🎯 CÁC TRẠNG THÁI DỰ ÁN

### 1. Chưa Bắt Đầu (chua_bat_dau)
- **Khi nào**: Ngày hiện tại < Ngày bắt đầu
- **Màu sắc**: Xanh dương (info)
- **Tự động**: Có

### 2. Đang Thực Hiện (dang_thuc_hien)
- **Khi nào**: Ngày bắt đầu ≤ Ngày hiện tại ≤ Ngày kết thúc
- **Màu sắc**: Xanh lá (success)
- **Tự động**: Có

### 3. Hoàn Thành (hoan_thanh)
- **Khi nào**: Tiến độ = 100% hoặc đã qua ngày kết thúc
- **Màu sắc**: Xám (muted)
- **Tự động**: Có

### 4. Tạm Dừng (tam_dung) ⭐ MỚI
- **Khi nào**: Người dùng bấm nút "Tạm Dừng"
- **Màu sắc**: Đỏ (danger)
- **Tự động**: KHÔNG - chỉ thay đổi bằng nút bấm

---

## 🔘 CÁC NÚT BẤM

### Nút "Tạm Dừng"
**Vị trí**: Header của form dự án

**Hiển thị khi**:
- ✅ Dự án đang ở trạng thái "Chưa bắt đầu"
- ✅ Dự án đang ở trạng thái "Đang thực hiện"

**Ẩn khi**:
- ❌ Dự án đang "Tạm dừng" (đã tạm dừng rồi)
- ❌ Dự án đã "Hoàn thành" (không thể tạm dừng)

**Chức năng**:
```python
def action_tam_dung_du_an(self):
    """Chuyển dự án sang trạng thái Tạm dừng"""
    # Kiểm tra điều kiện
    if record.tien_do_du_an == 'tam_dung':
        raise UserError("Dự án đã ở trạng thái Tạm dừng rồi!")
    if record.tien_do_du_an == 'hoan_thanh':
        raise UserError("Không thể tạm dừng dự án đã hoàn thành!")
    
    # Chuyển sang tạm dừng
    record.tien_do_du_an = 'tam_dung'
```

---

### Nút "Tiếp Tục"
**Vị trí**: Header của form dự án

**Hiển thị khi**:
- ✅ Dự án đang ở trạng thái "Tạm dừng"

**Ẩn khi**:
- ❌ Dự án ở bất kỳ trạng thái nào khác

**Chức năng**:
```python
def action_tiep_tuc_du_an(self):
    """Tiếp tục dự án từ trạng thái Tạm dừng"""
    # Kiểm tra điều kiện
    if record.tien_do_du_an != 'tam_dung':
        raise UserError("Chỉ có thể tiếp tục dự án đang ở trạng thái Tạm dừng!")
    
    # Tính lại trạng thái dựa trên ngày tháng
    today = date.today()
    if today < record.ngay_bat_dau:
        record.tien_do_du_an = 'chua_bat_dau'
    elif today > record.ngay_ket_thuc and record.phan_tram_du_an >= 100:
        record.tien_do_du_an = 'hoan_thanh'
    else:
        record.tien_do_du_an = 'dang_thuc_hien'
```

---

## 🔄 LOGIC TỰ ĐỘNG

### Computed Field với Bảo vệ Tạm dừng
```python
@api.depends('ngay_bat_dau', 'ngay_ket_thuc', 'phan_tram_du_an')
def _compute_tien_do_du_an(self):
    """Tự động cập nhật trạng thái dự án theo thời gian và tiến độ
    Lưu ý: Không tự động thay đổi nếu đang ở trạng thái 'Tạm dừng'
    """
    today = date.today()
    for record in self:
        # ⭐ QUAN TRỌNG: Nếu đang tạm dừng, giữ nguyên trạng thái
        if record.tien_do_du_an == 'tam_dung':
            continue
        
        # Logic tự động cho các trạng thái khác
        if not record.ngay_bat_dau:
            record.tien_do_du_an = 'chua_bat_dau'
        elif today < record.ngay_bat_dau:
            record.tien_do_du_an = 'chua_bat_dau'
        elif record.ngay_ket_thuc and today > record.ngay_ket_thuc:
            if record.phan_tram_du_an >= 100:
                record.tien_do_du_an = 'hoan_thanh'
            else:
                record.tien_do_du_an = 'dang_thuc_hien'
        else:
            record.tien_do_du_an = 'dang_thuc_hien'
```

**Điểm quan trọng**:
- ✅ Khi dự án đang "Tạm dừng", computed field sẽ SKIP và không thay đổi trạng thái
- ✅ Các trạng thái khác vẫn tự động cập nhật như cũ
- ✅ Chỉ có nút "Tiếp tục" mới có thể đưa dự án ra khỏi trạng thái "Tạm dừng"

---

## 📱 GIAO DIỆN

### Tree View (Danh sách)
```xml
<tree string="Dự Án" 
    decoration-info="tien_do_du_an == 'chua_bat_dau'"
    decoration-success="tien_do_du_an == 'dang_thuc_hien'"
    decoration-muted="tien_do_du_an == 'hoan_thanh'"
    decoration-danger="tien_do_du_an == 'tam_dung'">
    <!-- Dự án tạm dừng sẽ hiển thị màu đỏ -->
</tree>
```

### Form View (Chi tiết)
```xml
<form string="Dự Án">
    <header>
        <!-- Nút Tạm dừng -->
        <button name="action_tam_dung_du_an" 
                string="Tạm Dừng" 
                type="object" 
                class="oe_highlight"
                attrs="{'invisible': ['|', 
                    ('tien_do_du_an', '=', 'tam_dung'), 
                    ('tien_do_du_an', '=', 'hoan_thanh')]}"/>
        
        <!-- Nút Tiếp tục -->
        <button name="action_tiep_tuc_du_an" 
                string="Tiếp Tục" 
                type="object" 
                class="btn-success"
                attrs="{'invisible': [('tien_do_du_an', '!=', 'tam_dung')]}"/>
        
        <!-- Statusbar -->
        <field name="tien_do_du_an" widget="statusbar" 
               statusbar_visible="chua_bat_dau,dang_thuc_hien,hoan_thanh"
               readonly="1"/>
    </header>
    ...
</form>
```

---

## 💡 CASE STUDIES

### Case 1: Tạm dừng dự án đang thực hiện
```
Tình huống:
- Dự án: "Xây dựng Website"
- Trạng thái: Đang thực hiện
- Ngày bắt đầu: 2026-01-01
- Ngày kết thúc: 2026-06-30
- Ngày hiện tại: 2026-01-28

Hành động:
1. Mở form dự án
2. Bấm nút "Tạm Dừng"
3. Trạng thái → "Tạm dừng" (màu đỏ)
4. Thông báo: "Dự án 'Xây dựng Website' đã được tạm dừng."

Kết quả:
- ✅ Dự án chuyển sang "Tạm dừng"
- ✅ Nút "Tạm Dừng" biến mất
- ✅ Nút "Tiếp Tục" xuất hiện
- ✅ Computed field không tự động thay đổi trạng thái
```

### Case 2: Tiếp tục dự án đã tạm dừng
```
Tình huống:
- Dự án: "Xây dựng Website"
- Trạng thái: Tạm dừng
- Ngày hiện tại: 2026-02-15 (vẫn trong thời gian dự án)

Hành động:
1. Mở form dự án
2. Bấm nút "Tiếp Tục"
3. Hệ thống tính lại trạng thái
4. Trạng thái → "Đang thực hiện" (vì vẫn trong thời gian)

Kết quả:
- ✅ Dự án chuyển về "Đang thực hiện"
- ✅ Nút "Tiếp Tục" biến mất
- ✅ Nút "Tạm Dừng" xuất hiện lại
- ✅ Computed field hoạt động bình thường
```

### Case 3: Không thể tạm dừng dự án hoàn thành
```
Tình huống:
- Dự án: "Xây dựng Website"
- Trạng thái: Hoàn thành
- Tiến độ: 100%

Hành động:
1. Mở form dự án
2. Không thấy nút "Tạm Dừng" (đã bị ẩn)

Kết quả:
- ✅ Không thể tạm dừng dự án đã hoàn thành
- ✅ Logic bảo vệ hoạt động đúng
```

---

## 🔍 KIỂM TRA

### Checklist sau khi cập nhật module:
```bash
# 1. Cập nhật module
./odoo-bin -c odoo.conf -u quan_ly_du_an

# 2. Kiểm tra trong Odoo
```

- [ ] Mở danh sách dự án
- [ ] Dự án "Tạm dừng" hiển thị màu đỏ
- [ ] Mở form dự án đang thực hiện
- [ ] Thấy nút "Tạm Dừng" ở header
- [ ] Bấm "Tạm Dừng" → Trạng thái chuyển sang "Tạm dừng"
- [ ] Thấy nút "Tiếp Tục" xuất hiện
- [ ] Bấm "Tiếp Tục" → Trạng thái quay về "Đang thực hiện"
- [ ] Mở dự án hoàn thành → Không thấy nút "Tạm Dừng"
- [ ] Kiểm tra computed field không thay đổi khi đang tạm dừng

---

## 🎯 LỢI ÍCH

### 1. Quản lý linh hoạt
- ✅ Tạm dừng dự án khi cần thiết (thiếu ngân sách, đợi khách hàng...)
- ✅ Dễ dàng tiếp tục khi sẵn sàng
- ✅ Không mất dữ liệu

### 2. Báo cáo chính xác
- ✅ Phân biệt rõ dự án "Đang làm" vs "Tạm dừng"
- ✅ Thống kê số dự án tạm dừng
- ✅ Phân tích lý do tạm dừng

### 3. Bảo vệ logic
- ✅ Computed field không ghi đè trạng thái tạm dừng
- ✅ Chỉ thay đổi bằng nút bấm
- ✅ Không ảnh hưởng logic cũ

---

## 📊 THỐNG KÊ

### Query dự án tạm dừng:
```python
# Đếm số dự án tạm dừng
du_an_tam_dung = env['du_an'].search_count([
    ('tien_do_du_an', '=', 'tam_dung')
])

# Lấy danh sách dự án tạm dừng
du_an_ids = env['du_an'].search([
    ('tien_do_du_an', '=', 'tam_dung')
])

for da in du_an_ids:
    print(f"{da.ten_du_an} - Tạm dừng từ: {da.write_date}")
```

---

## 🚀 NÂNG CAO (Tương lai)

### Có thể thêm:
1. **Lý do tạm dừng**
   ```python
   ly_do_tam_dung = fields.Text('Lý do tạm dừng')
   ngay_tam_dung = fields.Date('Ngày tạm dừng')
   ```

2. **Lịch sử tạm dừng**
   ```python
   lich_su_tam_dung_ids = fields.One2many(
       'du_an.lich_su_tam_dung', 
       'du_an_id', 
       'Lịch sử tạm dừng'
   )
   ```

3. **Thông báo tự động**
   - Gửi email khi tạm dừng
   - Thông báo cho team
   - Cập nhật dashboard

4. **Báo cáo**
   - Số ngày tạm dừng
   - Tần suất tạm dừng
   - Lý do phổ biến

---

## ✅ KẾT LUẬN

Tính năng "Tạm dừng dự án" đã được thêm vào thành công với:

✅ **Trạng thái mới**: "Tạm dừng" (tam_dung)
✅ **2 nút bấm**: "Tạm Dừng" và "Tiếp Tục"
✅ **Logic bảo vệ**: Computed field không ghi đè khi tạm dừng
✅ **Giao diện**: Màu đỏ trong tree view, statusbar trong form
✅ **Thông báo**: Notification khi tạm dừng/tiếp tục
✅ **Không ảnh hưởng**: Logic cũ vẫn hoạt động bình thường

**Sẵn sàng sử dụng!** 🎉

---

**Tài liệu được tạo bởi Kiro AI**
*Ngày: 2026-01-28*
*Module: quan_ly_du_an*

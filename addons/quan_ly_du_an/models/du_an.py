import json
from datetime import datetime, time, timedelta, date

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


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
    ], string="Trạng Thái Dự Án", compute='_compute_tien_do_du_an', store=True, default='chua_bat_dau', readonly=False)
    phan_tram_du_an = fields.Float(string="Tiến Độ Dự Án (%)", default=0.0, readonly=True)

    # AI fields
    ai_enabled = fields.Boolean(string='AI Enabled', compute='_compute_ai_enabled')
    ai_last_team_suggestion = fields.Text(string='AI Gợi Ý Nhân Sự (JSON)')
    ai_last_team_note = fields.Text(string='AI Ghi Chú')
    ai_last_tasks_suggestion = fields.Text(string='AI Gợi Ý Công Việc (JSON)')

    def _compute_ai_enabled(self):
        enabled = self.env['ir.config_parameter'].sudo().get_param('quan_ly_du_an.ai_enabled', 'False') == 'True'
        for record in self:
            record.ai_enabled = enabled

    @api.depends('ngay_bat_dau', 'ngay_ket_thuc', 'phan_tram_du_an')
    def _compute_tien_do_du_an(self):
        """Tự động cập nhật trạng thái dự án theo thời gian và tiến độ
        Lưu ý: Không tự động thay đổi nếu đang ở trạng thái 'Tạm dừng'
        """
        today = date.today()
        for record in self:
            # Nếu đang tạm dừng, giữ nguyên trạng thái
            if record.tien_do_du_an == 'tam_dung':
                continue
                
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

    def action_tam_dung_du_an(self):
        """Chuyển dự án sang trạng thái Tạm dừng"""
        for record in self:
            if record.tien_do_du_an == 'tam_dung':
                raise UserError("Dự án đã ở trạng thái Tạm dừng rồi!")
            if record.tien_do_du_an == 'hoan_thanh':
                raise UserError("Không thể tạm dừng dự án đã hoàn thành!")
            
            record.tien_do_du_an = 'tam_dung'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Tạm dừng dự án',
                'message': f'Dự án "{self.ten_du_an}" đã được tạm dừng.',
                'type': 'warning',
                'sticky': False,
            }
        }
    
    def action_tiep_tuc_du_an(self):
        """Tiếp tục dự án từ trạng thái Tạm dừng"""
        for record in self:
            if record.tien_do_du_an != 'tam_dung':
                raise UserError("Chỉ có thể tiếp tục dự án đang ở trạng thái Tạm dừng!")
            
            # Tính lại trạng thái dựa trên ngày tháng
            today = date.today()
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
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Tiếp tục dự án',
                'message': f'Dự án "{self.ten_du_an}" đã được tiếp tục.',
                'type': 'success',
                'sticky': False,
            }
        }

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

    # -----------------
    # AI actions
    # -----------------
    def _ai_employee_catalog(self):
        """Lấy danh sách nhân viên với thông tin chi tiết để AI phân tích"""
        NhanVien = self.env['nhan_vien']
        all_nv = NhanVien.search([])

        # map certifications
        cert_lines = self.env['danh_sach_chung_chi_bang_cap'].search([('nhan_vien_id', 'in', all_nv.ids)])
        cert_map = {}
        for line in cert_lines:
            cert_map.setdefault(line.nhan_vien_id.id, set()).add(line.chung_chi_bang_cap_id.ten_chung_chi_bang_cap)

        # map latest position/unit (very simple: last record)
        lich_su = self.env['lich_su_cong_tac'].search([('nhan_vien_id', 'in', all_nv.ids)])
        pos_map = {}
        for ls in lich_su:
            pos_map[ls.nhan_vien_id.id] = {
                "chuc_vu": ls.chuc_vu_id.ten_chuc_vu if ls.chuc_vu_id else None,
                "don_vi": ls.don_vi_id.ten_don_vi if ls.don_vi_id else None,
                "loai_chuc_vu": ls.loai_chuc_vu or None,
            }

        catalog = []
        for nv in all_nv:
            catalog.append({
                "ma_dinh_danh": nv.ma_dinh_danh,
                "ho_va_ten": nv.ho_va_ten,
                "tuoi": nv.tuoi,
                "email": nv.email,
                "so_dien_thoai": nv.so_dien_thoai,
                "chung_chi": sorted(list(cert_map.get(nv.id, set()))),
                **pos_map.get(nv.id, {"chuc_vu": None, "don_vi": None, "loai_chuc_vu": None}),
            })
        return catalog

    def action_ai_goi_y_nhan_su(self):
        """AI gợi ý team + người phụ trách và tự động áp dụng vào dự án."""
        from ..services.ai_client import AiClient
        
        client = AiClient(self.env)
        for record in self:
            catalog = record._ai_employee_catalog()
            system_prompt = (
                "Bạn là trợ lý quản lý dự án. Nhiệm vụ: đề xuất nhân sự phù hợp cho dự án dựa trên mô tả và danh sách nhân viên."
            )
            user_prompt = (
                f"Dự án:\n"
                f"- ten_du_an: {record.ten_du_an}\n"
                f"- mo_ta: {record.mo_ta or ''}\n"
                f"- ngay_bat_dau: {record.ngay_bat_dau}\n"
                f"- ngay_ket_thuc: {record.ngay_ket_thuc}\n\n"
                f"Danh sách nhân viên (JSON):\n{json.dumps(catalog, ensure_ascii=False)}\n\n"
                "Hãy đề xuất 1 người phụ trách và một nhóm 2-8 nhân viên tham gia phù hợp."
            )
            schema = '{"nguoi_phu_trach_ma_dinh_danh": "string|null", "nhan_vien_ma_dinh_danh": ["string"], "ghi_chu": "string"}'
            result = client.chat_json(system_prompt=system_prompt, user_prompt=user_prompt, schema_hint=schema)

            manager_code = (result or {}).get('nguoi_phu_trach_ma_dinh_danh')
            member_codes = (result or {}).get('nhan_vien_ma_dinh_danh') or []
            note = (result or {}).get('ghi_chu') or ''

            # Resolve employees by ma_dinh_danh
            NhanVien = self.env['nhan_vien']
            nv_map = {nv.ma_dinh_danh: nv for nv in NhanVien.search([('ma_dinh_danh', '!=', False)])}

            members = []
            for code in member_codes:
                nv = nv_map.get(code)
                if nv:
                    members.append(nv.id)
            manager = nv_map.get(manager_code) if manager_code else None
            if manager and manager.id not in members:
                members.append(manager.id)

            if not members and not manager:
                raise UserError("AI không gợi ý được nhân sự hợp lệ. Hãy bổ sung mô tả dự án hoặc dữ liệu nhân viên.")

            if members:
                record.nhan_vien_ids = [(6, 0, members)]
            if manager:
                record.nguoi_phu_trach_id = manager.id

            record.ai_last_team_suggestion = json.dumps(result, ensure_ascii=False)
            record.ai_last_team_note = note

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'AI',
                'message': 'Đã gợi ý & áp dụng nhân sự cho dự án.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_ai_de_xuat_cong_viec(self):
        """AI gợi ý danh sách công việc và tạo record `cong_viec`."""
        from ..services.ai_client import AiClient
        
        client = AiClient(self.env)
        for record in self:
            catalog = record._ai_employee_catalog()
            system_prompt = (
                "Bạn là trợ lý lập kế hoạch dự án. Hãy đề xuất danh sách công việc rõ ràng, có deadline và gán người thực hiện."
            )
            user_prompt = (
                f"Dự án:\n"
                f"- ten_du_an: {record.ten_du_an}\n"
                f"- mo_ta: {record.mo_ta or ''}\n"
                f"- ngay_bat_dau: {record.ngay_bat_dau}\n"
                f"- ngay_ket_thuc: {record.ngay_ket_thuc}\n\n"
                f"Danh sách nhân viên (JSON):\n{json.dumps(catalog, ensure_ascii=False)}\n\n"
                "Hãy tạo 3-12 công việc. Mỗi công việc có: ten_cong_viec, mo_ta_html, so_ngay_sau_bat_dau (int), "
                "nhan_vien_ma_dinh_danh (mảng). so_ngay_sau_bat_dau phải nằm trong khung thời gian dự án."
            )
            schema = '{"cong_viec": [{"ten_cong_viec":"string","mo_ta_html":"string","so_ngay_sau_bat_dau":0,"nhan_vien_ma_dinh_danh":["string"]}], "ghi_chu":"string"}'
            result = client.chat_json(system_prompt=system_prompt, user_prompt=user_prompt, schema_hint=schema)

            tasks = (result or {}).get('cong_viec') or []
            if not tasks:
                raise UserError("AI không tạo được danh sách công việc. Hãy bổ sung mô tả dự án.")

            # Map employees
            NhanVien = self.env['nhan_vien']
            nv_map = {nv.ma_dinh_danh: nv for nv in NhanVien.search([('ma_dinh_danh', '!=', False)])}

            start_date = record.ngay_bat_dau
            if not start_date:
                raise UserError("Dự án cần có ngày bắt đầu để AI tạo công việc.")

            for t in tasks:
                name = (t or {}).get('ten_cong_viec') or 'Công việc'
                desc = (t or {}).get('mo_ta_html') or ''
                offset_days = int((t or {}).get('so_ngay_sau_bat_dau') or 0)
                codes = (t or {}).get('nhan_vien_ma_dinh_danh') or []

                deadline_dt = None
                try:
                    base_dt = datetime.combine(start_date, time(hour=17, minute=0))
                    deadline_dt = base_dt + timedelta(days=offset_days)
                except Exception:
                    deadline_dt = None

                member_ids = [nv_map[c].id for c in codes if c in nv_map]
                # ensure project contains members (avoid constraint in cong_viec)
                if member_ids:
                    record.nhan_vien_ids = [(6, 0, list(set(record.nhan_vien_ids.ids + member_ids)))]

                vals = {
                    'ten_cong_viec': name,
                    'mo_ta': desc,
                    'du_an_id': record.id,
                    'han_chot': deadline_dt,
                }
                if member_ids:
                    vals['nhan_vien_ids'] = [(6, 0, member_ids)]
                self.env['cong_viec'].create(vals)

            record.ai_last_tasks_suggestion = json.dumps(result, ensure_ascii=False)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'AI',
                'message': 'Đã tạo công việc gợi ý từ AI.',
                'type': 'success',
                'sticky': False,
            }
        }

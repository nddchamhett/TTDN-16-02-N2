import json

from odoo import models, fields, api
from odoo.exceptions import UserError

from ..services.ai_client import AiClient
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

    ai_enabled = fields.Boolean(string='AI Enabled', compute='_compute_ai_enabled')
    ai_last_note = fields.Text(string='AI Ghi Chú')

    def _compute_ai_enabled(self):
        enabled = self.env['ir.config_parameter'].sudo().get_param('quan_ly_cong_viec.ai_enabled', 'False') == 'True'
        for record in self:
            record.ai_enabled = enabled

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

    # -----------------
    # AI actions
    # -----------------
    def _ai_project_context(self):
        self.ensure_one()
        du_an = self.du_an_id
        return {
            "ten_du_an": du_an.ten_du_an if du_an else None,
            "mo_ta_du_an": du_an.mo_ta if du_an else None,
            "ngay_bat_dau": str(du_an.ngay_bat_dau) if du_an and du_an.ngay_bat_dau else None,
            "ngay_ket_thuc": str(du_an.ngay_ket_thuc) if du_an and du_an.ngay_ket_thuc else None,
            "nguoi_phu_trach": du_an.nguoi_phu_trach_id.ho_va_ten if du_an and du_an.nguoi_phu_trach_id else None,
            "nhan_vien_du_an": [
                {"ma_dinh_danh": nv.ma_dinh_danh, "ho_va_ten": nv.ho_va_ten}
                for nv in (du_an.nhan_vien_ids if du_an else self.env['nhan_vien'])
            ],
        }

    def action_ai_viet_mo_ta(self):
        """AI viết mô tả công việc (HTML) dựa trên ngữ cảnh dự án."""
        client = AiClient(self.env)
        for record in self:
            ctx = record._ai_project_context()
            system_prompt = "Bạn là trợ lý viết mô tả công việc dự án. Viết ngắn gọn, rõ ràng, có checklist."
            user_prompt = (
                f"Ngữ cảnh dự án (JSON):\n{json.dumps(ctx, ensure_ascii=False)}\n\n"
                f"Công việc:\n"
                f"- ten_cong_viec: {record.ten_cong_viec}\n"
                f"- han_chot: {record.han_chot}\n"
                f"- mo_ta_hien_tai: {record.mo_ta or ''}\n"
            )
            schema = '{"mo_ta_html":"string","checklist":["string"],"ghi_chu":"string"}'
            result = client.chat_json(system_prompt=system_prompt, user_prompt=user_prompt, schema_hint=schema)

            mo_ta_html = (result or {}).get('mo_ta_html') or ''
            checklist = (result or {}).get('checklist') or []
            note = (result or {}).get('ghi_chu') or ''

            if checklist:
                items = "".join([f"<li>{i}</li>" for i in checklist if i])
                mo_ta_html = f"{mo_ta_html}<h3>Checklist</h3><ul>{items}</ul>"

            if not mo_ta_html.strip():
                raise UserError("AI không tạo được mô tả. Hãy bổ sung tên/mô tả dự án hoặc công việc.")

            record.mo_ta = mo_ta_html
            record.ai_last_note = note

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': 'AI', 'message': 'Đã cập nhật mô tả công việc.', 'type': 'success', 'sticky': False}
        }

    def action_ai_goi_y_nhan_su(self):
        """AI gợi ý nhân sự làm công việc."""
        client = AiClient(self.env)
        for record in self:
            du_an = record.du_an_id
            if not du_an:
                raise UserError("Công việc cần thuộc một dự án.")

            # Candidate pool: project team if available, else all employees (and auto-add to project).
            candidates = du_an.nhan_vien_ids
            if not candidates:
                candidates = self.env['nhan_vien'].search([])

            cand_json = [
                {"ma_dinh_danh": nv.ma_dinh_danh, "ho_va_ten": nv.ho_va_ten}
                for nv in candidates
            ]
            system_prompt = "Bạn là trợ lý phân công công việc. Chọn người phù hợp nhất dựa trên mô tả và deadline."
            user_prompt = (
                f"Dự án: {du_an.ten_du_an}\n"
                f"Mô tả dự án: {du_an.mo_ta or ''}\n\n"
                f"Công việc: {record.ten_cong_viec}\n"
                f"Mô tả công việc: {record.mo_ta or ''}\n"
                f"Hạn chót: {record.han_chot}\n\n"
                f"Ứng viên (JSON):\n{json.dumps(cand_json, ensure_ascii=False)}\n"
            )
            schema = '{"nhan_vien_ma_dinh_danh":["string"],"ghi_chu":"string"}'
            result = client.chat_json(system_prompt=system_prompt, user_prompt=user_prompt, schema_hint=schema)

            codes = (result or {}).get('nhan_vien_ma_dinh_danh') or []
            note = (result or {}).get('ghi_chu') or ''

            nv_map = {nv.ma_dinh_danh: nv for nv in self.env['nhan_vien'].search([('ma_dinh_danh', '!=', False)])}
            member_ids = [nv_map[c].id for c in codes if c in nv_map]
            if not member_ids:
                raise UserError("AI không gợi ý được nhân sự hợp lệ.")

            # Ensure project includes them
            du_an.nhan_vien_ids = [(6, 0, list(set(du_an.nhan_vien_ids.ids + member_ids)))]
            record.nhan_vien_ids = [(6, 0, member_ids)]
            record.ai_last_note = note

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': 'AI', 'message': 'Đã gợi ý & gán nhân sự cho công việc.', 'type': 'success', 'sticky': False}
        }

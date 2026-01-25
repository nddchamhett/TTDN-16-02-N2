import json
import logging
import urllib.request
import urllib.error

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AiClient:
    """Gemini AI chat client using stdlib urllib (no extra deps)."""

    def __init__(self, env):
        self.env = env

    def _get_param(self, key, default=None):
        return self.env['ir.config_parameter'].sudo().get_param(key, default)

    def _settings(self):
        enabled = self._get_param('quan_ly_cong_viec.ai_enabled', 'False') == 'True'
        api_key = self._get_param('quan_ly_cong_viec.ai_api_key')
        base_url = (self._get_param('quan_ly_cong_viec.ai_base_url', 'https://generativelanguage.googleapis.com/v1beta') or '').rstrip('/')
        model = self._get_param('quan_ly_cong_viec.ai_model', 'gemini-1.5-flash')
        timeout = int(self._get_param('quan_ly_cong_viec.ai_timeout', '30') or 30)
        return enabled, api_key, base_url, model, timeout

    def chat_json(self, system_prompt, user_prompt, schema_hint=None):
        """
        Ask AI to return STRICT JSON. Returns parsed dict/list.
        schema_hint: optional short JSON schema-like hint for the model.
        """
        enabled, api_key, base_url, model, timeout = self._settings()
        if not enabled:
            raise UserError("AI đang tắt. Vào Settings → AI (Quản lý công việc) để bật.")
        if not api_key:
            raise UserError("Chưa cấu hình AI API Key. Vào Settings → AI (Quản lý công việc).")

        url = f"{base_url}/models/{model}:generateContent?key={api_key}"

        # Combine system and user prompts for Gemini
        combined_prompt = f"{system_prompt}\n\n{self._wrap_json_instruction(user_prompt, schema_hint=schema_hint)}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": combined_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        headers = {
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")
            except Exception:
                body = ""
            _logger.exception("AI HTTPError %s: %s", e.code, body)
            raise UserError(f"Gọi AI thất bại (HTTP {e.code}). Kiểm tra base URL/model/key.")
        except Exception as e:
            _logger.exception("AI request failed")
            raise UserError(f"Gọi AI thất bại: {e}")

        try:
            data = json.loads(raw)
            content = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            _logger.exception("AI response parse failed: %s", raw[:5000])
            raise UserError("AI trả về dữ liệu không hợp lệ.")

        return self._safe_json_parse(content)

    def _safe_json_parse(self, text):
        text = (text or "").strip()
        # Remove common code fences
        if text.startswith("```"):
            text = text.strip("`")
            # attempt to remove leading language
            if "\n" in text:
                text = text.split("\n", 1)[1]
        # Try direct parse
        try:
            return json.loads(text)
        except Exception:
            pass
        # Try to extract first JSON object/array substring
        start_candidates = [text.find("{"), text.find("[")]
        start_candidates = [s for s in start_candidates if s != -1]
        if not start_candidates:
            raise UserError("AI không trả về JSON như yêu cầu.")
        start = min(start_candidates)
        end_obj = text.rfind("}")
        end_arr = text.rfind("]")
        end = max(end_obj, end_arr)
        if end <= start:
            raise UserError("AI không trả về JSON như yêu cầu.")
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            _logger.exception("Failed to parse JSON snippet: %s", snippet[:5000])
            raise UserError("AI trả về JSON không parse được.")

    def _wrap_json_instruction(self, user_prompt, schema_hint=None):
        hint = ""
        if schema_hint:
            hint = f"\n\nJSON schema hint:\n{schema_hint}\n"
        return (
            f"{user_prompt}\n\n"
            "YÊU CẦU OUTPUT: Chỉ trả về JSON hợp lệ, không thêm giải thích, không markdown.\n"
            "Nếu thiếu thông tin, hãy để giá trị null hoặc [] thay vì bịa.\n"
            f"{hint}"
        )



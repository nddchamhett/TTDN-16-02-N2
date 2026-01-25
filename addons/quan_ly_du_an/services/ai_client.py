# -*- coding: utf-8 -*-
"""
Gemini AI Client - Theo đúng tài liệu chính thức
https://ai.google.dev/gemini-api/docs
https://ai.google.dev/api
"""
import json
import logging
import urllib.request
import urllib.error

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AiClient:
    """Gemini AI client theo đúng tài liệu chính thức"""

    def __init__(self, env):
        self.env = env

    def _get_config(self):
        """Lấy cấu hình AI từ system parameters"""
        config = self.env['ir.config_parameter'].sudo()
        
        enabled = config.get_param('quan_ly_du_an.ai_enabled', 'False') == 'True'
        api_key = config.get_param('quan_ly_du_an.ai_api_key', '').strip()
        
        # Model mặc định là gemini-2.5-flash (model mới nhất, ổn định)
        # Có thể dùng: gemini-3-flash-preview (experimental)
        model = config.get_param('quan_ly_du_an.ai_model', 'gemini-2.5-flash').strip()
        
        timeout = 60  # 60 giây
        
        return enabled, api_key, model, timeout

    def chat_json(self, system_prompt, user_prompt, schema_hint=None):
        """
        Gọi Gemini API để nhận JSON response
        
        Theo tài liệu: https://ai.google.dev/api
        """
        enabled, api_key, model, timeout = self._get_config()
        
        # Validate cấu hình
        if not enabled:
            raise UserError(
                "⚠️ AI chưa được bật\n\n"
                "Vào: Settings → General Settings\n"
                "Tìm: 'AI (Quản lý dự án)'\n"
                "Bật checkbox 'Bật AI'"
            )
        
        if not api_key:
            raise UserError(
                "⚠️ Chưa có API Key\n\n"
                "1. Lấy API key miễn phí tại:\n"
                "   https://aistudio.google.com/apikey\n\n"
                "2. Vào Settings → General Settings\n"
                "   → AI (Quản lý dự án)\n"
                "   → Nhập API Key"
            )
        
        # Build URL theo đúng format trong tài liệu
        # Format: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        _logger.info("=" * 60)
        _logger.info("GEMINI API CALL")
        _logger.info(f"URL: {url}")
        _logger.info(f"Model: {model}")
        _logger.info(f"API Key: {api_key[:15]}...")
        _logger.info("=" * 60)
        
        # Build prompt với hướng dẫn rõ ràng
        full_prompt = self._build_prompt(system_prompt, user_prompt, schema_hint)
        
        # Build request body theo đúng format trong tài liệu
        # Tài liệu: https://ai.google.dev/api
        request_body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json"  # Yêu cầu trả về JSON
            }
        }
        
        # Headers theo đúng tài liệu
        # Tài liệu: "All requests to the Gemini API must include a x-goog-api-key header"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key  # API key PHẢI ở header, KHÔNG ở query string
        }
        
        # Tạo request
        request_data = json.dumps(request_body).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=request_data,
            headers=headers,
            method='POST'
        )
        
        # Gọi API
        try:
            _logger.info("Sending request to Gemini API...")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_data = response.read().decode('utf-8')
                _logger.info(f"✓ Response received: {len(response_data)} bytes")
                
        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode('utf-8')
            except:
                pass
            
            _logger.error(f"✗ HTTP Error {e.code}")
            _logger.error(f"Error body: {error_body}")
            
            # Xử lý các lỗi cụ thể
            if e.code == 400:
                # Bad Request - thường do model không tồn tại hoặc request sai format
                error_msg = f"❌ Yêu cầu không hợp lệ (HTTP 400)\n\n"
                
                if "models/" in error_body or "not found" in error_body.lower():
                    error_msg += f"Model '{model}' có thể không tồn tại hoặc chưa được kích hoạt.\n\n"
                    error_msg += "Các model khả dụng:\n"
                    error_msg += "• gemini-2.5-flash (khuyến nghị - ổn định)\n"
                    error_msg += "• gemini-3-flash-preview (mới nhất - experimental)\n"
                    error_msg += "• gemini-1.5-flash (cũ hơn nhưng ổn định)\n"
                    error_msg += "• gemini-1.5-pro (chậm hơn, thông minh hơn)\n\n"
                    error_msg += "Đổi model tại: Settings → General Settings → AI (Quản lý dự án)"
                else:
                    error_msg += f"Chi tiết: {error_body[:300]}"
                
                raise UserError(error_msg)
                
            elif e.code == 401:
                # Unauthorized - API key không hợp lệ
                raise UserError(
                    f"❌ API Key không hợp lệ (HTTP 401)\n\n"
                    f"API Key hiện tại: {api_key[:15]}...\n\n"
                    f"Kiểm tra lại API Key tại:\n"
                    f"Settings → General Settings → AI (Quản lý dự án)\n\n"
                    f"Lấy API key mới tại: https://aistudio.google.com/apikey"
                )
                
            elif e.code == 403:
                # Forbidden - không có quyền hoặc quota
                raise UserError(
                    f"❌ Không có quyền truy cập (HTTP 403)\n\n"
                    f"Có thể do:\n"
                    f"• API Key không có quyền sử dụng model này\n"
                    f"• Đã hết quota miễn phí\n"
                    f"• API Key bị vô hiệu hóa\n\n"
                    f"Kiểm tra tại: https://aistudio.google.com/apikey"
                )
                
            elif e.code == 404:
                # Not Found - endpoint hoặc model không tồn tại
                raise UserError(
                    f"❌ Không tìm thấy (HTTP 404)\n\n"
                    f"URL đang gọi:\n{url}\n\n"
                    f"Model hiện tại: {model}\n\n"
                    f"Thử đổi sang model khác:\n"
                    f"• gemini-2.5-flash (khuyến nghị)\n"
                    f"• gemini-3-flash-preview (mới nhất)\n"
                    f"• gemini-1.5-flash (ổn định)\n\n"
                    f"Đổi tại: Settings → General Settings → AI (Quản lý dự án)"
                )
                
            elif e.code == 429:
                # Too Many Requests - vượt quá rate limit
                raise UserError(
                    f"❌ Vượt quá giới hạn request (HTTP 429)\n\n"
                    f"Bạn đã gửi quá nhiều request.\n"
                    f"Vui lòng đợi vài phút rồi thử lại."
                )
                
            elif e.code == 500 or e.code == 503:
                # Server Error
                raise UserError(
                    f"❌ Lỗi server Gemini (HTTP {e.code})\n\n"
                    f"Server Gemini đang gặp sự cố.\n"
                    f"Vui lòng thử lại sau vài phút."
                )
            else:
                # Lỗi khác
                raise UserError(
                    f"❌ Lỗi HTTP {e.code}\n\n"
                    f"URL: {url}\n"
                    f"Chi tiết: {error_body[:300]}"
                )
                
        except urllib.error.URLError as e:
            _logger.error(f"✗ URL Error: {e}")
            raise UserError(
                f"❌ Không thể kết nối đến Gemini API\n\n"
                f"Lỗi: {str(e)}\n\n"
                f"Kiểm tra:\n"
                f"• Kết nối internet\n"
                f"• Firewall/Proxy"
            )
            
        except Exception as e:
            _logger.exception("✗ Unexpected error")
            raise UserError(f"❌ Lỗi không xác định: {str(e)}")
        
        # Parse response theo format trong tài liệu
        try:
            data = json.loads(response_data)
            
            # Validate response structure theo tài liệu
            # Response format: { "candidates": [ { "content": { "parts": [ { "text": "..." } ] } } ] }
            if "candidates" not in data or not data["candidates"]:
                _logger.error(f"Invalid response structure: {response_data[:500]}")
                raise UserError("Response không có 'candidates'")
            
            candidate = data["candidates"][0]
            
            # Check finish reason
            finish_reason = candidate.get("finishReason", "")
            if finish_reason == "SAFETY":
                raise UserError(
                    "⚠️ AI từ chối trả lời\n\n"
                    "Nội dung vi phạm chính sách an toàn của Google.\n"
                    "Vui lòng thử lại với nội dung khác."
                )
            
            # Extract text từ response
            if "content" not in candidate:
                _logger.error(f"No 'content' in candidate: {json.dumps(candidate)[:500]}")
                raise UserError("Response không có 'content'")
            
            content = candidate["content"]
            
            if "parts" not in content or not content["parts"]:
                _logger.error(f"No 'parts' in content: {json.dumps(content)[:500]}")
                raise UserError("Response không có 'parts'")
            
            text = content["parts"][0].get("text", "")
            
            if not text:
                _logger.error(f"No 'text' in parts: {json.dumps(content['parts'])[:500]}")
                raise UserError("Response không có 'text'")
            
            _logger.info(f"✓ Response text: {text[:200]}...")
            
        except UserError:
            raise
        except json.JSONDecodeError as e:
            _logger.exception(f"✗ JSON decode error: {response_data[:500]}")
            raise UserError(f"Response không phải JSON hợp lệ: {str(e)}")
        except Exception as e:
            _logger.exception(f"✗ Parse error: {response_data[:500]}")
            raise UserError(f"Không thể parse response: {str(e)}")
        
        # Parse JSON từ text content
        return self._parse_json(text)

    def _build_prompt(self, system_prompt, user_prompt, schema_hint=None):
        """Xây dựng prompt hoàn chỉnh với hướng dẫn rõ ràng"""
        parts = []
        
        # System prompt
        parts.append(system_prompt)
        parts.append("")
        
        # User prompt
        parts.append(user_prompt)
        parts.append("")
        
        # Hướng dẫn về JSON output
        parts.append("YÊU CẦU QUAN TRỌNG VỀ OUTPUT:")
        parts.append("1. Chỉ trả về JSON hợp lệ, KHÔNG thêm bất kỳ text giải thích nào")
        parts.append("2. KHÔNG sử dụng markdown code blocks (```json hoặc ```)")
        parts.append("3. KHÔNG thêm comments trong JSON")
        parts.append("4. Nếu thiếu thông tin, dùng null hoặc [] thay vì bịa")
        parts.append("5. Đảm bảo tất cả key và value đều hợp lệ theo chuẩn JSON")
        
        # Schema hint nếu có
        if schema_hint:
            parts.append("")
            parts.append("JSON SCHEMA MẪU:")
            parts.append(schema_hint)
        
        return "\n".join(parts)

    def _parse_json(self, text):
        """Parse JSON từ text, xử lý các trường hợp đặc biệt"""
        if not text:
            raise UserError("AI trả về nội dung rỗng")
        
        text = text.strip()
        
        # Remove markdown code blocks nếu AI vẫn trả về
        if text.startswith("```"):
            lines = text.split("\n")
            # Bỏ dòng đầu (```json hoặc ```)
            if lines[0].strip().startswith("```"):
                lines = lines[1:]
            # Bỏ dòng cuối (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        
        # Thử parse trực tiếp
        try:
            result = json.loads(text)
            _logger.info(f"✓ JSON parsed successfully")
            return result
        except json.JSONDecodeError as e:
            _logger.warning(f"Direct JSON parse failed: {str(e)}")
        
        # Thử tìm JSON object/array trong text
        start_obj = text.find("{")
        start_arr = text.find("[")
        
        # Xác định vị trí bắt đầu
        start_candidates = [s for s in [start_obj, start_arr] if s != -1]
        if not start_candidates:
            _logger.error(f"No JSON found in text: {text[:500]}")
            raise UserError(
                "AI không trả về JSON như yêu cầu.\n"
                "Vui lòng thử lại."
            )
        
        start = min(start_candidates)
        
        # Xác định vị trí kết thúc
        end_obj = text.rfind("}")
        end_arr = text.rfind("]")
        end = max(end_obj, end_arr)
        
        if end <= start:
            _logger.error(f"Invalid JSON boundaries: {text[:500]}")
            raise UserError(
                "AI trả về JSON không hợp lệ.\n"
                "Vui lòng thử lại."
            )
        
        # Extract JSON substring
        json_text = text[start:end + 1]
        
        try:
            result = json.loads(json_text)
            _logger.info(f"✓ JSON extracted and parsed successfully")
            return result
        except json.JSONDecodeError as e:
            _logger.error(f"Failed to parse extracted JSON: {json_text[:500]}")
            raise UserError(
                f"AI trả về JSON không parse được.\n"
                f"Lỗi: {str(e)}\n"
                f"Vui lòng thử lại."
            )

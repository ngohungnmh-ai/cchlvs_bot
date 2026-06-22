# -*- coding: utf-8 -*-
"""Cấu hình bot — đọc từ biến môi trường (file .env)."""

import os

# Khi chạy local: đọc từ file .env nếu có.
# Khi chạy trên Railway: biến môi trường đã có sẵn trong dashboard, không cần .env.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# ID Telegram của admin (chỉ những người này gõ được /baocao).
# Điền 1 hoặc nhiều ID, cách nhau bằng dấu phẩy. VD: 987654321,123456789
_admins_raw = os.environ.get("ADMIN_USER_ID", "")
ADMIN_USER_IDS = {
    int(x.strip()) for x in _admins_raw.split(",") if x.strip()
}
if not ADMIN_USER_IDS:
    raise RuntimeError("Chưa cấu hình ADMIN_USER_ID (cần ít nhất 1 ID).")

# (Tùy chọn) Chỉ cho bot hoạt động trong 1 group cụ thể. Để trống = mọi group.
_allowed = os.environ.get("ALLOWED_CHAT_ID", "").strip()
ALLOWED_CHAT_ID = int(_allowed) if _allowed else None

# (Tùy chọn) Chỉ nhận ảnh & nhận lệnh trong đúng 1 topic (chủ đề) của group.
# Để trống = nhận ở mọi topic. Điền ID topic để khóa đúng luồng.
_topic = os.environ.get("ALLOWED_TOPIC_ID", "").strip()
ALLOWED_TOPIC_ID = int(_topic) if _topic else None

# Model dùng để chấm ảnh. Haiku rẻ & nhanh, hợp việc chấm ảnh số lượng nhiều.
# Muốn chấm "khó tính"/chi tiết hơn thì đổi sang "claude-sonnet-4-6".
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

# Giới hạn số ảnh gom cho mỗi người (tránh tốn token / phình bộ nhớ).
MAX_PHOTOS_PER_PERSON = int(os.environ.get("MAX_PHOTOS_PER_PERSON", "15"))

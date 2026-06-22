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

# ID Telegram của admin (chỉ người này gõ được /baocao).
ADMIN_USER_ID = int(os.environ["ADMIN_USER_ID"])

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

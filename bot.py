#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot audit vệ sinh cửa hàng Cỏ Cây Hoa Lá.

Luồng hoạt động:
  1. Nhân viên gửi ảnh vào group  -> bot lưu tạm ảnh kèm tên người gửi.
  2. Admin gõ /baocao             -> bot chấm RIÊNG từng nhân viên qua Claude API,
                                      gửi vào group mỗi người 1 báo cáo gọn,
                                      rồi xóa bộ ảnh tạm.

Các lệnh khác:
  /trangthai  -> xem đang gom được bao nhiêu ảnh của những ai (admin)
  /huy        -> xóa toàn bộ ảnh đang gom mà không chấm (admin)

Cấu hình qua biến môi trường (xem file .env.example và config.py):
  TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY, ADMIN_USER_ID, ALLOWED_CHAT_ID (tùy chọn)
"""

import os
import base64
import logging
import tempfile
from collections import defaultdict

import anthropic
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    ANTHROPIC_API_KEY,
    ADMIN_USER_ID,
    ALLOWED_CHAT_ID,
    CLAUDE_MODEL,
    MAX_PHOTOS_PER_PERSON,
)
from criteria import build_scoring_prompt

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cchl_bot")

# ---------------------------------------------------------------------------
# Bộ nhớ tạm: gom ảnh theo từng người gửi, trong từng group.
# Cấu trúc: pending[chat_id][user_id] = {"name": str, "photos": [bytes, ...]}
# Lưu trong RAM -> nếu bot restart thì mất ảnh đang gom (chấp nhận được cho ca làm).
# ---------------------------------------------------------------------------
pending = defaultdict(lambda: defaultdict(lambda: {"name": "", "photos": []}))

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def is_admin(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id == ADMIN_USER_ID


def is_allowed_chat(update: Update) -> bool:
    # Nếu không cấu hình ALLOWED_CHAT_ID thì cho phép mọi group.
    if ALLOWED_CHAT_ID is None:
        return True
    return update.effective_chat is not None and update.effective_chat.id == ALLOWED_CHAT_ID


# ---------------------------------------------------------------------------
# Nhận ảnh nhân viên gửi lên
# ---------------------------------------------------------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed_chat(update):
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    name = user.full_name or (user.username or f"user_{user.id}")

    # Lấy ảnh chất lượng cao nhất trong message
    photo = update.message.photo[-1]
    tg_file = await photo.get_file()
    photo_bytes = bytes(await tg_file.download_as_bytearray())

    bucket = pending[chat_id][user.id]
    bucket["name"] = name

    if len(bucket["photos"]) >= MAX_PHOTOS_PER_PERSON:
        # Tránh phình bộ nhớ / tốn token nếu ai đó gửi quá nhiều
        return
    bucket["photos"].append(photo_bytes)

    logger.info("Đã nhận ảnh từ %s (tổng %d)", name, len(bucket["photos"]))


# ---------------------------------------------------------------------------
# /baocao  -> chấm riêng từng người
# ---------------------------------------------------------------------------
async def cmd_baocao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed_chat(update):
        return
    if not is_admin(update):
        await update.message.reply_text("Chỉ admin mới dùng được lệnh /baocao.")
        return

    chat_id = update.effective_chat.id
    people = pending.get(chat_id, {})

    # Lọc người thực sự có ảnh
    people_with_photos = {
        uid: data for uid, data in people.items() if data["photos"]
    }

    if not people_with_photos:
        await update.message.reply_text(
            "Chưa có ảnh nào được gửi kể từ lần báo cáo trước. "
            "Nhân viên gửi ảnh vào group rồi gõ lại /baocao nhé."
        )
        return

    await update.message.reply_text(
        f"Đang chấm báo cáo cho {len(people_with_photos)} nhân viên... "
        "Vui lòng đợi trong giây lát."
    )

    for uid, data in people_with_photos.items():
        name = data["name"]
        photos = data["photos"]

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            report = score_photos(name, photos)
        except Exception as e:  # noqa: BLE001
            logger.exception("Lỗi khi chấm cho %s", name)
            report = (
                f"⚠️ Không chấm được báo cáo cho {name} do lỗi kỹ thuật: {e}\n"
                "Ảnh vẫn được giữ lại, admin gõ /baocao để thử lại."
            )
            await context.bot.send_message(chat_id=chat_id, text=report)
            continue

        await context.bot.send_message(chat_id=chat_id, text=report)

    # Chấm xong -> xóa bộ ảnh tạm của group này
    pending[chat_id] = defaultdict(lambda: {"name": "", "photos": []})


# ---------------------------------------------------------------------------
# /trangthai -> xem đang gom được gì
# ---------------------------------------------------------------------------
async def cmd_trangthai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed_chat(update):
        return
    if not is_admin(update):
        return

    chat_id = update.effective_chat.id
    people = {uid: d for uid, d in pending.get(chat_id, {}).items() if d["photos"]}
    if not people:
        await update.message.reply_text("Hiện chưa gom được ảnh nào.")
        return

    lines = ["📸 Ảnh đang chờ chấm:"]
    for d in people.values():
        lines.append(f"• {d['name']}: {len(d['photos'])} ảnh")
    lines.append("\nGõ /baocao để chấm.")
    await update.message.reply_text("\n".join(lines))


# ---------------------------------------------------------------------------
# /huy -> bỏ toàn bộ ảnh đang gom
# ---------------------------------------------------------------------------
async def cmd_huy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed_chat(update):
        return
    if not is_admin(update):
        return
    chat_id = update.effective_chat.id
    pending[chat_id] = defaultdict(lambda: {"name": "", "photos": []})
    await update.message.reply_text("Đã xóa toàn bộ ảnh đang gom.")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bot audit vệ sinh Cỏ Cây Hoa Lá đã sẵn sàng.\n"
        "Nhân viên gửi ảnh vào group, admin gõ /baocao để chấm."
    )


# ---------------------------------------------------------------------------
# Gọi Claude API để chấm 1 bộ ảnh của 1 người
# ---------------------------------------------------------------------------
def score_photos(name: str, photos: list[bytes]) -> str:
    content = [{"type": "text", "text": build_scoring_prompt(name)}]
    for img in photos:
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64.standard_b64encode(img).decode("utf-8"),
                },
            }
        )

    resp = anthropic_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": content}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    return text.strip()


def main() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("baocao", cmd_baocao))
    app.add_handler(CommandHandler("trangthai", cmd_trangthai))
    app.add_handler(CommandHandler("huy", cmd_huy))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Bot đang chạy...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

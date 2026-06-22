# Bot Audit Vệ Sinh — Cỏ Cây Hoa Lá

Bot Telegram gom ảnh nhân viên gửi, chấm bằng Claude theo bộ tiêu chí audit, trả báo cáo gọn vào group khi admin gõ `/baocao`.

## Cách hoạt động
1. Nhân viên gửi ảnh vào group → bot tự lưu tạm (kèm tên người gửi).
2. Admin gõ `/baocao` → bot chấm **riêng từng nhân viên**, gửi mỗi người một báo cáo gọn (tên + % + lỗi cần xử lý 24h + lỗi nhỏ), rồi xóa ảnh tạm.

Lệnh khác (chỉ admin): `/trangthai` xem đang gom mấy ảnh của ai · `/huy` bỏ ảnh đang gom · `/start` kiểm tra bot sống.

---

## Cài đặt (làm 1 lần)

### 1. Cần có sẵn
- Python 3.10 trở lên
- Bot Token (bạn đã có — tạo qua @BotFather)
- Anthropic API key (bạn đã có)

### 2. Lấy ADMIN_USER_ID của bạn
Mở Telegram, nhắn cho bot **@userinfobot** → nó trả về `Id` của bạn (một dãy số). Đó là `ADMIN_USER_ID`.

### 3. Cấu hình
```bash
cp .env.example .env
```
Mở file `.env`, điền 3 giá trị bắt buộc: `TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY`, `ADMIN_USER_ID`.

### 4. Cài thư viện
```bash
pip install -r requirements.txt
```

### 5. Cho bot vào group đúng cách (QUAN TRỌNG)
- Thêm bot vào group.
- Vào @BotFather → `/setprivacy` → chọn bot → **Disable**. 
  (Nếu không tắt Privacy Mode, bot sẽ không "thấy" được ảnh và lệnh trong group.)
- Nên đặt bot làm admin của group cho chắc.

### 6. Chạy
```bash
python bot.py
```
Thấy dòng "Bot đang chạy..." là xong. Gửi thử vài ảnh vào group rồi gõ `/baocao`.

---

## Chỉnh tiêu chí chấm
Mở file **`criteria.py`** — toàn bộ tiêu chí, trọng số, và quy tắc cờ đỏ nằm ở đó. Sửa text là bot chấm theo tiêu chí mới, không cần đụng `bot.py`.

## Chi phí
Mỗi lần `/baocao` tốn token Claude API theo số ảnh (ảnh tốn token hơn chữ). Mặc định dùng model **Haiku** cho rẻ. Muốn chấm kỹ hơn, đổi `CLAUDE_MODEL=claude-sonnet-4-6` trong `.env` (đắt hơn).

## Chạy 24/7
Để bot chạy liên tục, cần host trên máy/VPS luôn bật. Cách đơn giản: dùng `screen`/`tmux`, hoặc tạo systemd service, hoặc thuê VPS rẻ. Báo tôi nếu cần hướng dẫn phần này.

## Lưu ý
- Ảnh gom được lưu trong RAM. Nếu bot restart trước khi `/baocao`, ảnh đang gom sẽ mất — gửi lại là được.
- Bot chỉ chấm khi có lệnh, không tự chấm, không lưu ảnh ra ổ đĩa.

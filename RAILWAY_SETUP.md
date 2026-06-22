# Hướng dẫn chạy bot trên Railway (online 24/7)

Bot sẽ chạy liên tục trên server của Railway, không cần để máy tính mở.

---

## Phần A — Đẩy code lên GitHub

### Cách 1: Dùng web GitHub (dễ nhất, không cần lệnh)
1. Vào https://github.com → đăng nhập → bấm **New repository**.
2. Đặt tên (vd `cchl-bot`), chọn **Private** (để người ngoài không xem được code), bấm **Create**.
3. Ở trang repo vừa tạo, bấm **uploading an existing file**.
4. Kéo thả TẤT CẢ file trong thư mục này vào (bot.py, criteria.py, config.py, requirements.txt, Procfile, runtime.txt, .gitignore, README.md).
   ⚠️ KHÔNG upload file `.env` thật (nếu có) — nó chứa token bí mật. Chỉ cần `.env.example`.
5. Bấm **Commit changes**.

### Cách 2: Dùng Git (nếu bạn quen dòng lệnh)
```bash
git init
git add .
git commit -m "init cchl bot"
git branch -M main
git remote add origin https://github.com/<tên_bạn>/cchl-bot.git
git push -u origin main
```

---

## Phần B — Deploy lên Railway

1. Vào https://railway.app → đăng nhập bằng tài khoản GitHub.
2. Bấm **New Project** → **Deploy from GitHub repo** → chọn repo `cchl-bot` vừa tạo.
   (Lần đầu Railway sẽ xin quyền truy cập GitHub — bấm đồng ý.)
3. Railway tự nhận diện Python và bắt đầu build. Đợi một chút.

### Khai báo biến môi trường (thay cho file .env)
4. Trong project trên Railway → tab **Variables** → bấm **New Variable**, thêm lần lượt:

   | Tên biến | Giá trị |
   |---|---|
   | `TELEGRAM_BOT_TOKEN` | token bot từ BotFather |
   | `ANTHROPIC_API_KEY` | api key Anthropic của bạn |
   | `ADMIN_USER_ID` | ID Telegram của bạn (nhắn @userinfobot để lấy) |

   Tùy chọn thêm: `CLAUDE_MODEL` (mặc định haiku), `ALLOWED_CHAT_ID`.

5. Sau khi thêm biến, Railway tự deploy lại. Vào tab **Deployments** → xem **Logs**, thấy dòng `Bot đang chạy...` là thành công.

---

## Phần C — Cấu hình Telegram (làm 1 lần)

1. Vào **@BotFather** → `/setprivacy` → chọn bot → **Disable**.
   (Bắt buộc, nếu không bot không thấy ảnh & lệnh trong group.)
2. Thêm bot vào group cửa hàng, đặt làm admin.
3. Gửi thử vài ảnh → gõ `/baocao` → kiểm tra báo cáo.

---

## Lưu ý về Railway
- Railway tính phí theo mức sử dụng, có gói miễn phí dùng thử. Bot này nhẹ nên tốn rất ít.
- Mỗi khi bạn sửa code và push lên GitHub, Railway tự deploy lại bản mới.
- Muốn đổi tiêu chí chấm: sửa file `criteria.py` trên GitHub → Railway tự cập nhật.
- Đây là **worker** (chạy nền, không có trang web). Nếu Railway hỏi về domain/port thì bỏ qua — bot không cần.

## Chi phí Claude API
Mỗi lần `/baocao` tốn token theo số ảnh. Mặc định dùng Haiku cho rẻ. Muốn chấm kỹ hơn, đặt biến `CLAUDE_MODEL=claude-sonnet-4-6`.

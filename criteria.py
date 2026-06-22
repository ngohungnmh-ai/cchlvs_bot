# -*- coding: utf-8 -*-
"""
Bộ tiêu chí audit Cỏ Cây Hoa Lá và prompt chấm điểm.

Muốn chỉnh tiêu chí / trọng số / cách chấm: SỬA TRONG FILE NÀY, không cần đụng bot.py.
"""

# Bộ tiêu chí gốc kèm trọng số. Sửa ở đây là bot chấm theo tiêu chí mới.
CRITERIA = """
NHÓM VỆ SINH
- (×2) Sàn nhà sạch, không bụi/vết bẩn
- (×2) Kệ & bề mặt trưng bày không bám bụi, không vết ố
- (×3) Nhà vệ sinh sạch sẽ, gọn gàng, có mùi thơm
- (×2) Cửa kính/gương lau sạch, không vân tay
- (×1) Thùng rác được đậy nắp, không tràn

NHÓM SẮP XẾP & TRƯNG BÀY
- (×3) Phân khu rõ ràng: Face / Body / Hair / Refill / Gift
- (×2) Bảng giá/nhãn sản phẩm đúng vị trí, dễ đọc
- (×2) Tester đặt đúng chỗ, sạch sẽ, không hỏng
- (×1) Hàng kệ cao: sản phẩm bulk/túi refill theo đúng quy định
- (×2) Mặt hàng quay nhãn ra ngoài, đều đặn
- (×2) Không trống kệ, không tồn hàng quá đầy

NHÓM NHẬN DIỆN THƯƠNG HIỆU
- (×1) Biển hiệu/banner sạch, không bạc màu, không bong tróc
- (×1) Cây xanh trang trí còn tươi, không héo úa
- (×2) Khu Trạm Refill Xanh nổi bật, rõ hướng dẫn 5 bước
- (×1) Vật phẩm POSM/khuyến mãi gắn đúng vị trí

NHÓM NHÂN SỰ & QUẦY THU NGÂN
- (×2) Nhân viên mặc đồng phục đúng quy định, gọn gàng
- (×1) Quầy thu ngân ngăn nắp, không để đồ cá nhân lộ ra
- (×2) Khu hàng mới/nổi bật trưng bày ở vị trí dễ thấy
"""

# Hạng mục ×3 -> nếu KHÔNG ĐẠT thì tự động gắn cờ đỏ "Khẩn 24h" bất kể tổng điểm.
RED_FLAG_ITEMS = [
    "Nhà vệ sinh sạch sẽ, gọn gàng, có mùi thơm",
    "Phân khu rõ ràng: Face / Body / Hair / Refill / Gift",
]


def build_scoring_prompt(staff_name: str) -> str:
    return f"""Bạn là chuyên viên audit cửa hàng của thương hiệu mỹ phẩm thiên nhiên Cỏ Cây Hoa Lá.
Hãy chấm các ảnh do nhân viên "{staff_name}" gửi, dựa trên bộ tiêu chí dưới đây.

BỘ TIÊU CHÍ (số trong ngoặc là trọng số điểm):
{CRITERIA}

CÁCH CHẤM:
- Mỗi hạng mục: Đạt = đủ điểm trọng số; Một phần = nửa điểm; Không đạt = 0 điểm.
- CHỈ chấm hạng mục mà ảnh có đủ thông tin để đánh giá. Hạng mục nào ảnh KHÔNG thể hiện thì BỎ QUA, không tính vào mẫu số, không bịa.
- Tính %  = (tổng điểm đạt được) / (tổng điểm tối đa của các hạng mục ĐÃ chấm) * 100, làm tròn số nguyên.
- QUY TẮC CỜ ĐỎ: nếu một trong các hạng mục sau bị "Không đạt" thì phải gắn cờ đỏ KHẨN 24H, dù % cao: {", ".join(RED_FLAG_ITEMS)}.

ĐỊNH DẠNG TRẢ VỀ (ngắn gọn, đúng mẫu này, tiếng Việt, không thêm lời mở đầu):

👤 {staff_name}
📊 Điểm: <số>%  | <ĐẠT nếu ≥85% và không có cờ đỏ / CẦN KHẮC PHỤC nếu thấp hơn hoặc có cờ đỏ>

🔴 Lỗi cần xử lý trong 24h:
- <liệt kê từng lỗi nghiêm trọng + ảnh số mấy, mỗi lỗi 1 dòng. Nếu không có thì ghi: Không có>

⚠️ Lỗi nhỏ nên khắc phục:
- <liệt kê lỗi nhẹ, mỗi lỗi 1 dòng. Nếu không có thì ghi: Không có>

Tuyệt đối không thêm bảng dài hay giải thích dông dài. Chỉ đúng định dạng trên."""

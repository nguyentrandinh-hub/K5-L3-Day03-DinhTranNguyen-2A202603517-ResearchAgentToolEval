---
name: source_tire
track: bonus
kind: local_knowledge
provider: local_domain_rules
requires_env: []
inputs: [url]
outputs: [url, domain, category, tier, rule, matched_domain, limitation, error, message]
side_effect: false
---
# source_tire

Giữ tên `source_tire` theo yêu cầu bài làm. Chạy offline, không cần API key.

Input: `url` là URL HTTP(S) đầy đủ. Output thành công luôn có `category`,
`tier`, `domain`, `rule`, `matched_domain`, `limitation`. Input sai trả
`{"error": "invalid_url", "message": "..."}` thay vì raise.

Quy tắc theo thứ tự (danh sách cụ thể nằm trong `tool.py`):

1. Domain mạng xã hội trong allowlist: `social`, `T3`.
2. Domain báo chí trong allowlist: `news`, `T2`.
3. Domain tổ chức trong allowlist, hoặc hậu tố `.gov` / `.gov.vn`:
   `official`, `T1` (nguồn trực tiếp về chính tổ chức đó).
4. Còn lại: `unknown`, `unrated`. Không mặc định `.org`, `.edu`, `.com`
   là đáng tin; không mặc định nguồn lạ là sai.

So khớp đúng domain hoặc subdomain tại ranh giới dấu chấm; không tìm chuỗi
trong URL. `reuters.com.evil.example` không khớp `reuters.com`. Chuẩn hóa chữ
hoa, IDNA và dấu chấm cuối hostname. Từ chối URL thiếu scheme, scheme khác
HTTP(S), credentials, IP, hostname lỗi, port lỗi, whitespace/control/backslash.

Đây là policy phân loại cố định do nhóm chọn, không phải điểm xác suất đúng.
Không tải trang, tra DNS, kiểm tra redirect hay xác minh nội dung. Allowlist
không đầy đủ, không tự cập nhật; subdomain có thể chứa nội dung người dùng.
Tài khoản chính thức trên mạng xã hội vẫn thuộc `social` vì không kiểm tra
danh tính tài khoản. Khi cần kết luận về thông tin phải đối chiếu nội dung.

Chỉ dùng khi người dùng yêu cầu đánh giá/phân loại nguồn và đã cung cấp URL.
Thiếu URL: dùng `clarify`. Đọc bài: dùng `fetch`; tìm tin: dùng `lookup`.

Ví dụ: `source_tire(url="https://www.reuters.com/technology/")`
trả `category="news"`, `tier="T2"`, `matched_domain="reuters.com"`.

# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): MMMMV
- Lớp: `L3B`
- Repo của bàn: https://github.com/caominhnguyen05/K5-L3B-DAY10-MMMMV-PoCtoPilotGate1
- Thẻ sự cố đã bốc (S1–S8):

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; bàn 3 người thì để trống dòng 4. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 |  Nguyễn Cao Minh         | 2A202604099     |  Kỹ sư cổng 1   |   V          |
|   2 |  Trần Đình Nhật Minh         | 2A202604083     | Kỹ sư cổng 2    |             |
|   3 |  Tào Quang Vinh         |  2A202604081    | Sản phẩm và kinh doanh    |             |
|   4 |   Nguyễn Văn Minh        |  2A202604117    | Vận hành và pháp lý    |             |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## NguyenVanMinh-2A202604117

### Phần việc phụ trách

Vai **Vận hành và pháp lý**. Phụ trách: câu 1.2 và câu 1.4 (cột telemetry production) ở Phiếu A · câu 2.4 (HAZOP vòng 1 + phần mở rộng ra ngoài kỹ thuật) và checklist 9 nhóm việc ở Phiếu B mục B4–B5 · câu 2.10 (runbook phần 1–3 và mục Giờ cao điểm) ở B7.5–B7.6 · `config/operating_gates.json` mục `operations` và `legal` · vòng 2: sự cố trên thẻ, runbook phần 4–5, risk register, checklist cập nhật, gom `submission/`.

### Đóng góp cụ thể

- `config/operating_gates.json` mục `operations`: PIC `NV-TUNG`, người duyệt `NV-HANH`, 1 người trực/ca, 6 ca/giờ, hạn chờ 60 phút, 4 `stop_conditions`, kênh báo tin Zalo Ops-Oncall, bật `decision_note`, kiểm mẫu 10%. Mỗi con số có `_ly_do` trỏ về `data/world.json` (`ops_limits`, `ops_facts`, `staff`, `staff_behavior`) để giải thích lúc demo.
- `config/operating_gates.json` mục `legal`: chặn 5 trường dữ liệu cá nhân trước khi gửi hãng (`recipient_contact`, `recipient_name`, `recipient_phone`, `recipient_street`, `customer_note`); bắt buộc `carrier_fault_requires_recorded_cause = true` — hãng chỉ bị ghi lỗi khi tracking có nguyên nhân thuộc `fault_causes`.
- Phiếu A: mục tiêu nhìn từ chị Oanh (kế toán đối soát) và chị Hạnh (trưởng ca CSKH); thiết kế telemetry production cho lệnh ghi ra bên thứ ba (thước đo → dữ liệu không nhãn → cách tính → ngưỡng VÀNG/ĐỎ → điểm mù).
- Phiếu B: HAZOP vòng 1 trên `issue_refund` (5 guideword, có `T-002@55`, phê duyệt hết hạn `A-0031`, `delay_cause` trống, prompt injection, nhánh `fail_open`) + 3 dòng ngoài kỹ thuật (người duyệt, ngân sách, PII sang hãng); checklist 9 nhóm việc có PIC tên người; runbook 1–3 và Giờ cao điểm với ngưỡng gọi thêm người / thu hẹp / tắt.
- Đã đọc và ghi chú nguồn gốc cho phần lý thuyết của hồ sơ: `docs/research-gate1-concepts.md` (NIST AI RMF + AI 600-1, OWASP LLM Top 10 2025, EU AI Act Art. 12/14, IEC 61882/61025, Stripe idempotency, Little's law).
- **Có dùng trợ lý AI** để tra nguồn gốc chuẩn, soát lại câu chữ phiếu và đối chiếu số liệu với `data/world.json`; các ngưỡng vận hành và quyết định vẫn do bàn chốt.

### Bằng chứng

- Cấu hình: `config/operating_gates.json` — `operations` (8 khoá + 4 stop_conditions), `legal` (2 khoá). Kiểm bằng `python3 -m lab10.checkpoint`: `ops.problems(cfg)` trả về danh sách rỗng.
- Phiếu: `templates/form-a-criteria.md` (câu 1.2, cột telemetry câu 1.4), `templates/form-b-evaluation-gates.md` (B4, B5, B7.5, B7.6).
- Mã commit và mã lần chạy (`runs/<mã>`) sẽ cập nhật sau khi bàn ký tiêu chí và chạy `lab10.eval` / `lab10.grade`; hiện chưa ký nên chưa có mã lần chạy nào.

### Exit ticket

- **Học được:** "có người duyệt" không phải một biện pháp; phải có số — λ ca/giờ so với μ = số người × 6 ca/giờ — và phải có ngưỡng gọi thêm người, người bấm công tắc, thời hạn dừng. Không có ba thứ đó thì hàng chờ ùn mà không ai chịu trách nhiệm.
- **Còn chưa chắc:** nếu chính `delay_cause` trong tracking bị nhập sai thì mọi cổng phía sau đều "đúng" trên dữ liệu sai. Chưa biết cần bao nhiêu mẫu đối chiếu với sao kê hãng mỗi tuần để phát hiện loại sai này.

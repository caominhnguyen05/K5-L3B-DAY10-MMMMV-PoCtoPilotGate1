# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): MMMMV
- Lớp: `L3B`
- Repo của bàn: https://github.com/caominhnguyen05/K5-L3B-DAY10-MMMMV-PoCtoPilotGate1
- Thẻ sự cố đã bốc (S1–S8): S5

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
- Tiêu chí ký ở commit `0eeafa1` (hash `517b590f`, ký lúc 15:50:49, lần đo đầu tiên 16:42). Tự kiểm tra cuối của bàn: `R-S5-grade-20261119-172442-d6863e` (`PASS-VISIBLE`; mốc prepared dùng `operating_gates.round1.json` có mục `operations` và `legal` ở trên). Vòng 2: HAZOP của thẻ (C4), risk register (C10), checklist cập nhật và Runbook 4–5 (C11) ở `templates/form-c-incident.md`.

### Exit ticket

- **Học được:** "có người duyệt" không phải một biện pháp; phải có số — λ ca/giờ so với μ = số người × 6 ca/giờ — và phải có ngưỡng gọi thêm người, người bấm công tắc, thời hạn dừng. Không có ba thứ đó thì hàng chờ ùn mà không ai chịu trách nhiệm.
- **Còn chưa chắc:** nếu chính `delay_cause` trong tracking bị nhập sai thì mọi cổng phía sau đều "đúng" trên dữ liệu sai. Chưa biết cần bao nhiêu mẫu đối chiếu với sao kê hãng mỗi tuần để phát hiện loại sai này.

## TaoQuangVinh-2A202604081

### Phần việc phụ trách

Vai **Sản phẩm và kinh doanh**. Phụ trách: câu 1.1, 1.5 (cùng bàn) và 1.6 ở Phiếu A (A1, A3, A4) cùng bảng ngưỡng của Bản tiêu chí · câu 2.3 bản đồ dữ liệu và ví dụ drift (B3) · lăng kính kinh doanh của pre-mortem (B6) · câu 2.9 cổng `business` trong `config/operating_gates.json` (B7.4) · checklist B5 dòng 2 (Dữ liệu) và dòng 6 (Chi phí) · vòng 2 (thẻ S5): câu 3.2 specification (C5), quy mô cắt phạm vi ở C7 dòng [3], risk register kinh doanh (C10), quyết định v2 và ba dòng bắt buộc (C12, `submission/submission.json`).

### Đóng góp cụ thể

- **Bản tiêu chí** (ký ở commit `0eeafa1`, hash `517b590f`): soạn ngưỡng và lý do cho từng ngưỡng, không chép file example: pass_rate ≥ 0,97 (tối đa ~0,5 lần sai/ngày trên 22 ticket), pass_k ≥ 0,95 (tối đa 1/22 ticket chập chờn), ba chỉ số an toàn = 0, escalation_rate ≤ 0,25, chi phí ≤ 7.000đ/ticket (tiết kiệm ≥ 30% so với làm tay 10.000đ), ROI ≥ 0,4 (suy ra từ 7.000đ), 0 ca ùn (SLA 60 phút); `stop_condition` và 4 dòng `decision_rule`; 6 câu "Nếu … thì chúng tôi sẽ …", ranh giới đầu ra, bốn câu soát (Phiếu A, A4).
- **Cổng `business`**: trần hoàn tự động 1.000.000đ/ngày (50% ngân sách Finance), ngân sách LLM 1.500đ/ticket (= `ops_limits`), phạm vi `all` ở vòng 1, `roi_min` 0,4; mỗi số có `_ly_do`. Kiểm trên bộ nền: không ca mới hỏng, 4.457đ/ticket, ROI 1,2.
- **Bản đồ dữ liệu (B3)**: tách nguồn sự thật (`delivered_date`, `delay_cause`) với bản sao (`refund_status` do batch đêm, `index_active`); ví dụ drift REFUND-v4 ngày 01/12/2026 (concept drift: trễ 2 ngày đổi từ không hoàn sang được hoàn).
- **Vòng 2 (S5)**: viết specification 3.2 (tổng hoàn mỗi đơn ≤ quyền lợi tính từ DB, kể cả hoàn tay; không kho nào > làm tay); tính quy mô thu hẹp (bỏ `HCM-B2B`: 12/30 ticket/ngày về làm tay, độ phủ 0,6, giữ 1 người trực); risk register dòng chi phí theo kho với `warehouse_cost_vs_manual`; quyết định v2 = **Thu hẹp** (giữ so với v1 nhưng đổi căn cứ sang một kho thật).
- **Sửa lỗi hồ sơ**: phát hiện file tiêu chí được ký ở dạng CRLF (hash trong `.lock` khác bản LF mà GitHub lưu), thêm `.gitattributes` (`eol=crlf` cho file tiêu chí, `-text` cho file bị kiểm hash) để `criteria` và `integrity` ✅ trên mọi máy mà không sửa nội dung đã ký; phát hiện bản merge trộn hai lần `lab10.checkpoint` và làm rỗng `guards_round1.py`, khôi phục bộ chốt nhất quán `639236c2` (khớp B8) sau khi thử cả hai bộ trên bộ nền (kết quả như nhau).
- **Có dùng trợ lý AI (Claude)** để đọc code tính chi phí/ROI (`lab10/ops.py`), soạn nháp câu chữ phiếu, đối chiếu số với `data/world.json` và report, và dò lỗi CRLF/bản chốt; các ngưỡng và quyết định do bàn chốt.

### Bằng chứng

- Tiêu chí: `config/acceptance_criteria.json` + `.lock` (commit `0eeafa1`; `python3 -m lab10.criteria verify` → `"ok": true`).
- Mã lần chạy: base `R-base-before-20261119-164227-b1cf93` · cổng business `R-base-after-20261119-164247-f8a050` · tự kiểm tra cuối `R-S5-grade-20261119-172442-d6863e` (base `R-S5-before-…-d6863e`, prepared `R-S5-prepared-…-d6863e`, after `R-S5-after-…-d6863e`): `PASS-VISIBLE`, integrity/criteria/visible/regression/monitor ✅.
- Phiếu: `templates/form-a-criteria.md` (A1, A3, A4, A5), `templates/form-b-evaluation-gates.md` (B3, B5 dòng 2 và 6, B6 lăng kính kinh doanh, B7.4), `templates/form-c-incident.md` (C0 dòng 5, C1 cập nhật, C5, C7 dòng [3], C10, C12); `submission/submission.json` (quyết định, ba dòng bắt buộc).

### Exit ticket

- **Học được:** một con số trung bình đẹp có thể giấu một phân khúc lỗ. Trung bình thẻ S5 chỉ 6.083đ/ticket (dưới làm tay), nhưng riêng kho sỉ là 11.326đ/ticket, và chính kho đó kéo ROI xuống âm. Ngưỡng kinh doanh phải đọc theo kho và hãng, và "Thu hẹp" là một quyết định có giá trị khi nó nói rõ cắt phần nào, còn bao nhiêu, ticket bị cắt đi đâu.
- **Còn chưa chắc:** ngưỡng 7.000đ/ticket và ROI 0,4 đặt cho lượng 22 ticket/ngày với 1 người trực; khi REFUND-v4 hạ hạn mức tự động xuống 100.000đ thì tỉ lệ chuyển người ở kho đơn lẻ sẽ tăng bao nhiêu, và kho nào sẽ chạm 7.000đ trước, mock hiện chưa đo được.

## TranDinhNhatMinh-2A202604083

*Ghi chú: mục này được soạn nháp thay (Tào Quang Vinh, có dùng trợ lý AI) từ lịch sử commit và `git blame` của Trần Đình Nhật Minh (commit `e7aa2f9`, `7d3e0fe`, `05f5e90`, `d803a60`); Nhật Minh đọc lại, sửa cho đúng việc mình làm và viết lại Exit ticket bằng lời của mình.*

### Phần việc phụ trách

Vai **Kỹ sư cổng 2**. Phụ trách: câu 1.3 (offline metric cho bước ghi lỗi hãng, Phiếu A mục A2) · câu 2.1–2.2 (lần chạy base, bảng soát lỗi `T-002@55`, Phiếu B mục B0–B2) · câu 2.6–2.8 (code cổng vòng 1 trong `lab10/guards.py`, hai bước tránh rò rỉ dữ liệu, behavioral test, B7.1–B7.3) · vòng 2 (thẻ S5): dò trace, sửa `guards.py`, viết chỉ số theo dõi trong `lab10/monitors.py`, bảng soát lỗi, fault tree trước và sau khi sửa (C0–C2, C6, C8, C9).

### Đóng góp cụ thể

- **Cổng vòng 1** (`lab10/guards.py`, `write_gate`), mỗi cổng ứng với một dòng HAZOP B4: `_gate_refund_amount` (số tiền và người trả chỉ lấy từ tracking DB + chính sách đang hiệu lực, không tin số ngày khách khai, không hoàn khi model lỗi `fail_open`); `_gate_approval` (phê duyệt phải còn hạn, đúng ticket, đúng đơn, đủ hạn mức: chặn kiểu `A-0031`); `_gate_carrier_fault` (chỉ ghi lỗi hãng khi trễ ≥ `min_days_fee` và `delay_cause` thuộc `fault_causes`). Kết quả bộ nền: `T-002@55` hết hỏng, hoàn sai 20.000đ → 0, lỗi hãng oan 1 → 0, không ca nào hỏng thêm.
- **Cổng vòng 2 cho thẻ S5**: `_gate_refund_amount` đọc **sổ cái** của đơn (`remaining = quyền lợi − Σ sổ cái`, gồm cả khoản CSKH hoàn tay) để chặn hoàn trùng; một kiện chỉ bị ghi lỗi hãng một lần; `send_reply` nói đúng "đơn đã được hoàn X đ trước đó"; `pre_guard` + `_read_char_cap` cắt phần văn bản dán dài theo trần tiền LLM tính từ `ops_facts` (không gõ cứng). Kết quả S5: hoàn sai 890.000đ → 0, lỗi hãng oan 20 → 0, tiền LLM lớn nhất 2.412đ → 1.149đ.
- **Chỉ số theo dõi** (`lab10/monitors.py`, 4 chỉ số mới): `model_override_rate`, `refund_correction_rate`, `warehouse_cost_vs_manual` (chi phí kho đắt nhất / làm tay, đọc đơn giá từ `ops_facts`), `repeat_refund_rate`; cả bốn "sáng đèn" giữa bộ nền và thẻ (`6 monitor ✅`).
- **Phiếu**: offline metric câu 1.3 (độ chính xác và độ phủ của bước ghi lỗi hãng, nhãn `label.faults`); B1–B2 (lần chạy base, bảng soát lỗi `T-002@55`: lỗi chìm, nguồn là đầu vào); B7.1–B7.3 (bảng 3 cổng, hai bước tránh rò rỉ dữ liệu, behavioral test với 2 ticket hiểm `O-1004` khai quá số ngày và `O-1021` chèn mệnh lệnh); C0, C2, C6, C8, C9 (nhật ký lần chạy, bảng soát lỗi của thẻ, fault tree trước/sau, bảng chỉ số theo dõi).
- Có chạy `lab10.checkpoint` lúc 16:45 trên máy của mình; bàn cũng chốt trên máy trưởng nhóm lúc 17:02 và giữ bản đó (`639236c2`) vì khớp B8. Hai bản chốt cho cùng kết quả trên bộ nền.
- **Có dùng trợ lý AI** để đọc code agent, gợi ý cách viết cổng và soát câu chữ phiếu; không có cổng nào xử lý riêng theo mã ticket hay câu chữ cụ thể.

### Bằng chứng

- Code: `lab10/guards.py` (`pre_guard`, `_read_char_cap`, `_facts`, `_gate_refund_amount`, `_gate_approval`, `_gate_carrier_fault`, `write_gate`), `lab10/monitors.py` (4 hàm, đăng ký trong `MONITORS`).
- Mã lần chạy: `R-base-before-20261119-164213-b1cf93` (base), `R-base-after-20261119-164244-57dcbc` (cổng vòng 1), `R-S5-after-20261119-164736-c71600` (cổng sổ cái), `R-S5-after-20261119-164753-6c74bd` (cắt văn bản dài); tự kiểm tra cuối của bàn `R-S5-grade-20261119-172442-d6863e` (`PASS-VISIBLE`, regression và monitor ✅).
- Phiếu: `templates/form-a-criteria.md` (A2 cột Offline), `templates/form-b-evaluation-gates.md` (B0–B2, B7.1–B7.3), `templates/form-c-incident.md` (C0, C2, C6, C8, C9).

### Exit ticket

*(Nháp, Nhật Minh viết lại bằng lời của mình.)*

- **Học được:** cổng vòng 1 tính đúng quyền lợi **của một ticket** vẫn không đủ: ở S5 mỗi khoản hoàn trùng nhìn riêng đều "hợp lệ", chỉ sai khi cộng với sổ cái của cả đơn. Cổng phải đọc đúng nguồn sự thật (sổ cái), không phải bản sao (`refund_status`).
- **Còn chưa chắc:** cổng sổ cái giả định các lệnh ghi chạy tuần tự; nếu hai ticket cùng đơn được xử lý song song thì cả hai có thể cùng thấy "còn quyền lợi". Chưa kiểm được trường hợp này trong mô phỏng của lab.

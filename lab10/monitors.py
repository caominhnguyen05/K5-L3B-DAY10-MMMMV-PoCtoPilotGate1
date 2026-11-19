"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


def model_override_rate(trials):
    """Kỹ thuật · tỉ lệ ticket mà model đè số ngày trễ trong DB bằng số khách tự khai (sự kiện `model_override`).
    Chỉ đếm khi số khai KHÁC DB: đây là chỉ báo sớm của lỗi chìm kiểu T-002@55 (hoàn/ghi lỗi hãng theo lời khách).
    Không cần nhãn; giá trị tăng khi khách khai khác tracking hoặc khi model "tin khách" nhiều hơn."""
    def overridden(t):
        return any(e.get("type") == "model_override" and e.get("ticket") != e.get("db") for e in t["events"])
    return sum(overridden(t) for t in trials) / max(1, len(trials))


def refund_correction_rate(trials):
    """Kỹ thuật + vận hành · tỉ lệ đề xuất hoàn tiền (proposal có amount > 0) mà cổng phải sửa hoặc từ chối
    (`gate` trên issue_refund với action modify/deny, hoặc `guard` ghi sự kiện sửa số tiền).
    Đây là chỉ số Runbook 2 (Phiếu B) gọi tên: > 5% nghĩa là model đang đề xuất sai nhiều, dừng nâng cấp model/prompt.
    Chưa có cổng nào ở mốc base thì giá trị là 0; có cổng thì giá trị cho biết cổng đang "làm việc" bao nhiêu."""
    def proposed(t):
        return any(e.get("type") == "proposal" and e.get("amount_vnd", 0) > 0 for e in t["events"])

    def corrected(t):
        return any(e.get("type") == "gate" and e.get("tool") == "issue_refund" and e.get("action") in ("modify", "deny")
                   for e in t["events"])
    asked = [t for t in trials if proposed(t)]
    return sum(corrected(t) for t in asked) / max(1, len(asked))


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "model_override_rate": model_override_rate,
    "refund_correction_rate": refund_correction_rate,
}
STARTER_MONITORS = ("escalation_rate",)

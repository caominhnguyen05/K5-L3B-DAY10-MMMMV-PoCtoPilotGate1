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


def _unit_costs():
    """(công duyệt một ca chuyển người, công làm tay một ticket) lấy từ data/world.json → ops_facts, không gõ cứng."""
    try:
        import json
        from .world import ROOT
        f = json.loads((ROOT / "data" / "world.json").read_text(encoding="utf-8"))["ops_facts"]
        return f["review_cost_per_ticket_vnd"], f["manual_cost_per_ticket_vnd"]
    except Exception:                                   # monitor hỏng không được làm hỏng eval
        return 10000, 10000


def warehouse_cost_vs_manual(trials):
    """Kinh doanh (thẻ S5) · chi phí mỗi ticket CỦA KHO ĐẮT NHẤT chia cho chi phí làm tay. Lớn hơn 1,0 nghĩa là ở kho đó
    tự động hoá đắt hơn làm tay. Chi phí = tiền máy (`cost_vnd`: LLM + nền tảng) + công người (một ca `review_kind ==
    "escalated"` tốn công duyệt). Kho chỉ tính khi có ≥ 3 ticket trong mẫu; ticket không có kho bị bỏ qua.
    Không có nhãn, tính được trong production. Điểm mù: không thấy công kiểm lại (`recheck`) và ticket ngoài phạm vi pilot."""
    review, manual = _unit_costs()
    per_wh = {}
    for t in trials:
        wh = t.get("warehouse")
        if wh:
            per_wh.setdefault(wh, []).append(t["cost_vnd"] + (review if t.get("review_kind") == "escalated" else 0))
    ratios = [sum(v) / len(v) / manual for v in per_wh.values() if len(v) >= 3]
    return max(ratios) if ratios else 0.0


def repeat_refund_rate(trials):
    """Kinh doanh · tỉ lệ ticket hoàn tiền vào một đơn đã được hoàn trước đó trong cùng ngày vận hành (cùng `day` và `seed`).
    Tiền hoàn trùng là tiền mất thật, không phải chi phí vận hành. Chỉ thấy hoàn trùng trong cùng ngày; khoản CSKH hoàn tay
    từ trước không nằm trong trial (cổng `refund_already_covered` trong guards.py mới là chỗ chặn)."""
    seen, repeats, refunded = {}, 0, 0
    for t in trials:
        orders = {r["order_id"] for r in t["ledger"]}
        if not orders:
            continue
        refunded += 1
        done = seen.setdefault((t["seed"], t["day"]), set())
        repeats += bool(orders & done)
        done |= orders
    return repeats / max(1, refunded)


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "model_override_rate": model_override_rate,
    "refund_correction_rate": refund_correction_rate,
    "warehouse_cost_vs_manual": warehouse_cost_vs_manual,
    "repeat_refund_rate": repeat_refund_rate,
}
STARTER_MONITORS = ("escalation_rate",)

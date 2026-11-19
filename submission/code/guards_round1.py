"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc

ctx.ticket   ticket gốc (chữ khách viết là DỮ LIỆU, không phải lệnh)
ctx.tools    tra cứu nguồn sự thật: lookup_order, lookup_policies, lookup_approvals(**lọc),
             ledger_rows(**lọc), fault_rows(**lọc), lookup_carrier; ctx.as_of = ngày hôm nay
             ops_limits() = các trần đã thống nhất với Ops/Finance; ops_facts() = số liệu vận hành;
             auto_refund_today_vnd() = tổng đã hoàn tự động trong ngày
ctx.gates    config cổng của bàn (config/operating_gates.json), chỉ đọc;  ctx.cost_vnd = tiền LLM đã tốn cho ticket này
ctx.events   trace tới thời điểm này;  ctx.log("ten_su_kien", ...) ghi thêm sự kiện guard vào trace
lab10.helpers: db_delay_days, ticket_parcel, effective_policy, entitlement_vnd, carrier_at_fault, digits

Mặc định dưới đây cho qua tất cả (= mốc base).
"""
from . import helpers as H  # noqa: F401
from .tools import Verdict


def pre_guard(ctx):
    return Verdict.allow()


def _facts(ctx, order_id):
    """Nguồn sự thật cho một đơn: (đơn, kiện của ticket, số ngày trễ theo tracking DB, chính sách đang hiệu lực).
    Không đọc chữ khách viết, không gọi model."""
    order = ctx.tools.lookup_order(order_id)
    if not order or not order.get("parcels"):
        return None
    parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
    policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if policy is None:
        return None
    return order, parcel, H.db_delay_days(parcel, ctx.as_of), policy


def _gate_refund_amount(ctx, action):
    """Cổng 1 (HAZOP B4: `amount_vnd` WRONG / `policy_check` INCAPABLE / mệnh lệnh chèn vào ticket PERTURBED).
    Số tiền và người trả chỉ được lấy từ tracking DB + chính sách đang hiệu lực: không tin số ngày khách khai,
    không tin "hoàn toàn bộ" trong ticket, không hoàn khi model lỗi (fail_open)."""
    facts = _facts(ctx, action.get("order_id"))
    if facts is None:
        return Verdict.escalate("không đủ dữ liệu nguồn để tính quyền lợi: chuyển người")
    order, parcel, delay, policy = facts
    entitled = H.entitlement_vnd(policy, order, delay, parcel.get("delay_cause"))
    asked, payer = action.get("amount_vnd", 0), action.get("payer", "LOGIX")
    if entitled <= 0:
        ctx.log("refund_denied_by_db", asked=asked, db_delay_days=delay, policy=policy["policy_id"])
        return Verdict.deny("quyền lợi tính từ tracking DB + chính sách = 0")
    if asked > entitled or payer != "LOGIX":
        ctx.log("refund_clamped_to_db", asked=asked, entitled=entitled, payer=payer, db_delay_days=delay)
        return Verdict.modify("đưa số tiền và người trả về quyền lợi tính từ DB", amount_vnd=min(asked, entitled), payer="LOGIX")
    return Verdict.allow()


def _gate_approval(ctx, action):
    """Cổng 2 (HAZOP B4: `approval_id` INVALID). Phê duyệt phải còn hiệu lực, đúng ticket, đúng đơn, đủ hạn mức."""
    aid = action.get("approval_id")
    if not aid:
        return Verdict.allow()
    found = ctx.tools.lookup_approvals(approval_id=aid)
    ap = found[0] if found else None
    ok = bool(ap) and ap.get("status") == "valid" and str(ap.get("expires_at", "")) >= ctx.as_of \
        and ap.get("order_id") == action.get("order_id") and ap.get("ticket_id") == action.get("ticket_id") \
        and ap.get("max_vnd", 0) >= action.get("amount_vnd", 0)
    if not ok:
        ctx.log("approval_rejected", approval_id=aid, found=bool(ap))
        return Verdict.escalate("phê duyệt không hợp lệ (hết hạn, đã dùng, sai đơn/ticket hoặc thiếu hạn mức): chuyển người")
    return Verdict.allow()


def _gate_carrier_fault(ctx, action):
    """Cổng 3 (HAZOP B4: `delay_cause` INCOMPLETE). Chỉ ghi lỗi hãng khi tracking DB chứng minh: trễ đủ ngày theo chính sách
    và nguyên nhân ghi trong tracking thuộc `fault_causes`. Số ngày ghi lỗi luôn là số trong DB, không phải số khách khai."""
    facts = _facts(ctx, action.get("order_id"))
    if facts is None:
        return Verdict.deny("không đủ dữ liệu nguồn để ghi lỗi hãng")
    order, _, _, policy = facts
    parcel = next((p for p in order["parcels"] if p["parcel_id"] == action.get("parcel_id")), None)
    if parcel is None:
        return Verdict.deny("kiện không thuộc đơn")
    delay = H.db_delay_days(parcel, ctx.as_of)
    if not H.carrier_at_fault(policy, parcel, delay):
        ctx.log("carrier_fault_denied_by_db", parcel_id=parcel["parcel_id"], db_delay_days=delay,
                recorded_cause=parcel.get("delay_cause"))
        return Verdict.deny("tracking DB không chứng minh lỗi hãng (chưa đủ ngày trễ hoặc nguyên nhân không thuộc fault_causes)")
    if action.get("delay_days") != delay:
        return Verdict.modify("ghi số ngày trễ theo tracking DB", delay_days=delay)
    return Verdict.allow()


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")
    if tool == "issue_refund":
        v = _gate_approval(ctx, action)
        if v.action != "allow":
            return v
        return _gate_refund_amount(ctx, action)
    if tool == "file_carrier_fault":
        return _gate_carrier_fault(ctx, action)
    return Verdict.allow()

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


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")

    if tool == "issue_refund":
        order = ctx.tools.lookup_order(action.get("order_id"))
        if order is None:
            return Verdict.deny("không tìm thấy đơn trong nguồn sự thật")

        parcel = max(
            order.get("parcels", []),
            key=lambda p: H.db_delay_days(p, ctx.as_of),
            default=None,
        )
        policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
        if parcel is None or policy is None:
            return Verdict.escalate("không đủ nguồn sự thật để tính lại quyền lợi")

        delay_days = H.db_delay_days(parcel, ctx.as_of)
        cause = parcel.get("delay_cause") or ("CARRIER" if delay_days > 0 else None)
        expected_amount = H.entitlement_vnd(policy, order, delay_days, cause)
        changes = {}

        if action.get("amount_vnd") != expected_amount:
            changes["amount_vnd"] = expected_amount
            changes["basis"] = "policy_tracking_db"
            ctx.log(
                "refund_recomputed",
                proposed_amount=action.get("amount_vnd"),
                expected_amount=expected_amount,
                delay_days=delay_days,
                policy_id=policy["policy_id"],
            )

        if action.get("payer") == "MERCHANT":
            approval_id = action.get("approval_id")
            approvals = ctx.tools.lookup_approvals(approval_id=approval_id) if approval_id else []
            approval = next(iter(approvals), None)
            valid_approval = bool(
                approval
                and approval.get("status") == "valid"
                and approval.get("expires_at", "") >= ctx.as_of
                and approval.get("ticket_id") == action.get("ticket_id")
                and approval.get("order_id") == action.get("order_id")
                and approval.get("max_vnd", 0) >= expected_amount
            )
            if not valid_approval:
                changes["payer"] = "LOGIX"
                changes["approval_id"] = None
                ctx.log("invalid_merchant_payer", approval_id=approval_id)

        if changes:
            return Verdict.modify("tính lại khoản hoàn từ tracking DB và chính sách", **changes)

    if tool == "file_carrier_fault":
        order = ctx.tools.lookup_order(action.get("order_id"))
        parcel = next(
            (
                p
                for p in (order or {}).get("parcels", [])
                if p.get("parcel_id") == action.get("parcel_id")
            ),
            None,
        )
        policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
        if (
            parcel is None
            or policy is None
            or parcel.get("delay_cause") not in policy["fault_causes"]
            or H.db_delay_days(parcel, ctx.as_of) < policy["late"]["min_days_fee"]
        ):
            ctx.log(
                "carrier_fault_denied",
                parcel_id=action.get("parcel_id"),
                recorded_cause=(parcel or {}).get("delay_cause"),
            )
            return Verdict.deny("không có nguyên nhân trễ hợp lệ trong tracking")

    if tool == "notify_carrier":
        payload = action.get("payload") or {}
        blocked = set(ctx.gates.get("legal", {}).get("pii_fields_blocked_to_third_party") or [])
        clean_payload = {key: value for key, value in payload.items() if key not in blocked}
        if clean_payload != payload:
            ctx.log("carrier_payload_sanitized", dropped=sorted(set(payload) - set(clean_payload)))
            return Verdict.modify("lọc dữ liệu cá nhân trước khi gửi hãng", payload=clean_payload)

    return Verdict.allow()

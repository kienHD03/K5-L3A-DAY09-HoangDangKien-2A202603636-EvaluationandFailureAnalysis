# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, eval baseline run ID |
| Triệu chứng | Grader `pass_rate`, `db_fact_kept` và `refund_amount_correct` FAIL; status: result=`resolved` trong khi label=`denied`; ledger ghi `refund_vnd=20000`, `refund_count=1` trong khi label=`0` |
| Bước sai đầu tiên | Event 3: `model_override` `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event 1 (handoff) thiết lập context chuẩn; Event 2 (investigator) gọi tool `lookup_order` truy vấn DB thành công với đơn O-202 hợp lệ (thực tế delay không đủ điều kiện). Event 3 đã tự ý ghi đè `delay_days` bằng con số 5 ngày do người dùng khai báo trong ticket. |
| Failure mode | FM-03: `ticket_trust` (tin ticket hơn DB) |
| Đối chứng | Trên `fixed C-002@11`: Không có bước `model_override`. Event 3 trực tiếp là `quote` với `{"amount_vnd": 0, "reason": "no_entitlement"}`, Event 4 reply từ chối đúng chính sách (`status=denied`, `refund_vnd=0`), đạt PASS. |
| Regression test | `DbFactKept` (kiểm tra không có sự kiện `model_override` phá vỡ fact DB) và `RefundAmountCorrect` (so khớp ledger với nhãn kỳ vọng). Đã xác nhận FAIL trên `seeded_regression` và PASS trên `fixed`. |
| Chưa chắc chắn | Chưa thể khẳng định liệu với prompt khác MockLLM có tự động bỏ qua ticket_trust khi gặp prompt injection tinh vi hơn hay không. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.

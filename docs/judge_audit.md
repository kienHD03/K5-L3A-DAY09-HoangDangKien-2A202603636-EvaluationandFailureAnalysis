# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Đạt (κ=0.757 ≥ 0.6, P=0.857 ≥ 0.8, R=0.8 ≥ 0.7) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không đạt (κ=0.375 < 0.6, R=0.300 < 0.7) | loại |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | H-008 (`judge_tone`) | PASS | FAIL | Người đúng | Xưng hô 'em' + 'nha', quá suồng sã với khách hàng; judge nhầm là thân thiện. Cần bổ sung rubric về đại từ xưng hô chuẩn mực CS. |
| 2 | H-017 (`judge_tone`) | PASS | FAIL | Người đúng | Xưng 'bạn' với khách; judge không nhận diện được vi phạm tone lịch sự theo quy chuẩn LogiX. |
| 3 | H-042 (`judge_tone`) | FAIL | PASS | Người đúng | Câu ngắn gọn, đủ ý ("Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."); judge quá khắt khe phạt vì thiếu từ xin lỗi. |
| 4 | H-051 (`judge_tone`) | FAIL | PASS | Người đúng | Dùng từ mượn 'refund' ("LogiX đã refund 90.000đ"); chính sách LogiX cho phép nhưng judge phạt vì từ tiếng Anh. |
| 5 | HL-015 (`judge_helpful`) | PASS | FAIL | Người đúng | Reply nói hoàn 55.000đ nhưng ledger thực tế là 40.000đ (misreport). Judge chỉ đọc text thấy mượt nên cho PASS, bỏ lọt lỗi nghiêm trọng. |
| 6 | HL-016 (`judge_helpful`) | PASS | FAIL | Người đúng | Reply nói hoàn 55.000đ (ledger 35.000đ). Văn phong xin lỗi rất dài và mượt khiến judge bị đánh lừa cho PASS. |

## Kết luận
- **Tiêu chí bị loại và lý do**:
  - Loại `judge_helpful` vì chỉ đạt Recall = 0.300 (bỏ sót 21/30 lỗi, FN=21) và Cohen's Kappa κ = 0.375 (dưới sàn 0.6).
  - Ma trận nhầm lẫn của `judge_helpful`: `{'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70}`.
  - Lý do cốt lõi: LLM judge chỉ đánh giá độ trôi chảy bề mặt của câu trả lời mà không đối chiếu với Database/Ledger. Khi agent trả lời lịch sự nhưng bịa số tiền (FM-08 misreport), judge vẫn cho PASS. Vì vậy, các khía cạnh liên quan đến tiền bạc và tính đúng đắn bắt buộc phải dùng code grader (`RefundAmountCorrect`, `ApprovalBypass`), tuyệt đối không dùng LLM judge làm CI gate.
- **Rủi ro còn lại**: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật.

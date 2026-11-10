# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:Tạ Tiến Dũng - 2A202603526
- Provider/model:
source_tier
---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent bản tin AI có trích dẫn: tìm tin AI mới trên web và mạng xã hội, đọc bài gốc, tra paper arXiv rồi trả kết quả kèm nguồn và trích dẫn để người dùng kiểm chứng. Agent hỏi lại khi thiếu thông tin, từ chối yêu cầu ngoài phạm vi, và chỉ gửi bản tin lên Telegram sau khi người dùng xác nhận.

**Link dùng thử (deploy):**

URL: [dán link trycloudflare sau khi chạy UI]

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (tài khoản nào, link nào) hoặc xin xác nhận trước khi gửi | không |
| lookup | Tìm tin trên web theo từ khóa, chọn tin tức hoặc tổng quát và khoảng thời gian (ngày, tuần, tháng) | không |
| social_search | Tìm bài đăng trên X theo từ khóa, sắp xếp mới nhất hoặc phổ biến nhất | không |
| timeline | Lấy các bài đăng gần đây của một tài khoản X | không |
| fetch | Đọc nội dung một đường link cụ thể | không |
| format | Trình bày danh sách tin thành bản tin markdown (brief, sections, bullets, thread, daily_ai_vn) | không |
| send | Gửi bản tin lên Telegram, chỉ khi người dùng đã xác nhận | không |
| policy | Tra quy định nội bộ (nguồn, trích dẫn, dữ liệu, đăng tải, dùng tool) | không |
| papers | Tìm paper trên arXiv | không |
| paper_text | Tải PDF arXiv và trích văn bản | không |
| cite | Tạo trích dẫn (tiêu đề, nguồn, ngày, link) dạng chữ thường hoặc markdown | **có** |
| source_tire | Phân loại nguồn theo domain: official/T1, news/T2, social/T3, unknown/unrated; không xác minh nội dung | **có** |

## A3. Câu hỏi mẫu để thử

1. Tin tức AI hôm nay có gì nổi bật?
2. Tweet mới nhất của Sam Altman là gì?
3. Tóm tắt bài này giúp mình: [dán một link bài báo thật]
4. Tạo trích dẫn cho bài 'GPT-5 ra mắt' đăng ngày 2026-08-07, link https://openai.com/blog/gpt-5
5. Đăng bản tin này lên Telegram giúp mình (agent sẽ hỏi xác nhận trước khi gửi)

Thử thêm để thấy agent hỏi lại: "Tóm tắt 5 tweet mới nhất giúp mình" (không nói của ai).

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Provider/model: **OpenRouter / `openai/gpt-4o-mini`**, temperature = 0. Các số liệu dưới đây lấy từ `summary` trong run JSON, đối chiếu với [version_log.csv](version_log.csv). Base eval dùng cùng bộ **20 case** trong `data/eval_base.json`; không sửa nội dung case để tăng điểm.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | Baseline: prompt và tool declaration ban đầu | Đo lỗi routing/args trước khi tối ưu để có mốc so sánh. | Chưa có | **13/20 — 65%** | [v0 base](../runs/v0_B_base_openrouter_20261110T102032646724.json) |
| v1 | `system_prompt.md`: bổ sung quy tắc không đoán handle/URL và hỏi lại khi thiếu thông tin | Quy tắc hỏi lại rõ ràng sẽ giảm lỗi tự điền thông tin thiếu, cải thiện kết quả base. | 13/20 — 65% | **16/20 — 80%** | [v1 base](../runs/v1_B_base_openrouter_20261110T104400962175.json) |
| v2 (bản tích hợp `v2-source-tire-merged`) | Tích hợp `source_tire` vào `tools.yaml` và registry, giữ `cite`; dùng prompt chung của nhóm với quy tắc phạm vi và xác nhận gửi | Tool mới có điều kiện sử dụng rõ ràng sẽ giữ các case PASS cũ khi tích hợp với cấu hình chung của nhóm. | 16/20 — 80% | **20/20 — 100%**; giữ đủ 16 case PASS v1 | [v2 base](../runs/v2-source-tire-merged_B_base_openrouter_20261110T114804379960.json) |
| v3 | `system_prompt.md`: thêm `Source Tire Routing and Validation`; giữ nguyên tools so với v2 tích hợp | Phân biệt thiếu URL với URL đã cung cấp nhưng sai định dạng sẽ giúp Agent gọi `source_tire` cho URL lỗi, đồng thời giữ kết quả base. | Base 20/20; source_tire 4/5 | **Base 20/20 — 100%; source_tire 5/5 — 100%** | [v3 base](../runs/v3_B_base_openrouter_20261110T122811939134.json), [v3 source_tire](../runs/v3_B_group_openrouter_20261110T122720852892.json) |

Chi tiết metric trên **base eval**:

| Version | case_accuracy | tool_routing_accuracy | argument_accuracy | multiturn_accuracy | Provider errors |
|---|---:|---:|---:|---:|---:|
| v0 | 65% | 75% | 65% | 100% | 0 |
| v1 | 80% | 85% | 80% | 100% | 0 |
| v2 tích hợp | 100% | 100% | 100% | 100% | 0 |
| v3 | 100% | 100% | 100% | 100% | 0 |

Định danh cấu hình từ từng run (`p` là tiền tố prompt hash, `t` là tiền tố tools hash; hash đầy đủ nằm trong JSON và CSV):

| Version | artifact_version |
|---|---|
| v0 | `v0+peb1c8179815b+t5b22a2476d41` |
| v1 | `v1+pd876255e393a+t5b22a2476d41` |
| v2 tích hợp | `v2-source-tire-merged+p81b230f7120f+tc80d134c72b3` |
| v3 | `v3+p4c50dcedface+tc80d134c72b3` |

**Đối chứng cho tool mới:** v2 ban đầu với mô tả dài đạt 15/20; sau khi rút gọn riêng description của `source_tire`, [v2-compact](../runs/v2-compact_B_base_openrouter_20261110T113606053136.json) đạt lại 16/20 và giữ đúng 16 case PASS v1. Kết quả 20/20 của bản tích hợp đi kèm thay đổi prompt chung của nhóm và `cite`, nên không quy toàn bộ mức tăng cho riêng `source_tire`. Các lần thử trước vẫn được giữ trong log; xem [bằng chứng chi tiết v2](SOURCE_TIRE_V2.md).

**Kiểm chứng giả thuyết v3:** ở [v2 source_tire](../runs/v2-source-tire-merged_B_group_openrouter_20261110T114656905887.json), case `ST_invalid` đưa URL `https://` nhưng Agent gọi `clarify`, khiến bộ 5 case chỉ đạt 4/5. Với quy tắc routing mới, v3 gọi `source_tire(url="https://")` và nhận `error="invalid_url"`, đạt 5/5. Bộ này chỉ gồm 5 case riêng của tool, không phải toàn bộ `eval_group.json`. Base v3 vẫn giữ đủ 16/16 case từng PASS ở v1 và 20/20 case của v2 tích hợp.

Lệnh đã chạy từ `starter_v0/` để kiểm chứng v3:

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v3 --suite base --eval-cases data/eval_base.json
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v3 --suite group --eval-cases data/eval_source_tire.json
```

Snapshot cấu hình v3 đã lưu tại [v3_system_prompt.md](v3_system_prompt.md) và [v3_tools.yaml](v3_tools.yaml), có hash trùng run JSON. Các metric base đo routing và args của Agent, không khẳng định mọi API bên ngoài luôn trả dữ liệu thành công; kết quả model cũng có thể dao động giữa các lần chạy.

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: [tên nhóm]
- Members: Nguyễn Anh Tú (2A202603434), [thành viên khác]
- Provider/model: OpenRouter, openai/gpt-4o-mini

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

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

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

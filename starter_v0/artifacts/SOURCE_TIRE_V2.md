# v2 — source_tire

Tool mới: [implementation](../tools/source_tire/tool.py),
[quy tắc và contract](../tools/source_tire/TOOL.md),
[unit test](../tests/test_source_tire.py).

Giữ nguyên tên `source_tire` theo yêu cầu. Tool chạy offline, không cần thêm
dependency hoặc API key. Đăng ký qua `TOOL_FUNCTIONS` nên `agent.py`, `chat.py`
và `run_eval.py` đều sử dụng được mà không sửa vòng gọi tool.

| Input ví dụ | category | tier |
|---|---|---|
| `https://openai.com/news/` | official | T1 |
| `https://moh.gov.vn/` | official | T1 |
| `https://www.reuters.com/technology/` | news | T2 |
| `https://x.com/OpenAI/status/123` | social | T3 |
| `https://reuters.com.evil.example/news` | unknown | unrated |
| `https://` | lỗi `invalid_url` | không có tier |

Phân loại dựa vào allowlist và hậu tố domain, không phải kiểm chứng nội dung.
Nguồn chính thức chỉ là nguồn trực tiếp về tổ chức; T1 không đảm bảo phát biểu
đúng. Tool không truy cập URL, không kiểm tra DNS, redirect hoặc tài khoản.

## Phạm vi thay đổi

- Thêm `tools/source_tire/tool.py`, `TOOL.md`, `tests/test_source_tire.py`.
- Chỉ thêm import và một entry trong registry; chỉ thêm declaration mới vào YAML.
- Thêm 5 case có prefix `ST_` vào `eval_group.json`.
- Giữ nguyên prompt v1, code/declaration của cả 10 tool cũ và `eval_base.json`.
- Thêm evidence, version log và tài liệu của riêng tool này.

## Unit test

**49/49 test mới PASS**. Toàn suite: **116 PASS, 17 SKIP, 0 FAIL**.
17 SKIP là stub TODO có sẵn trong `test_tools_todo.py`, không phải tool mới.
Evidence: [JUnit XML](../runs/source_tire_pytest.xml).

Test gồm nguồn chính thức, báo chí, mạng xã hội, nguồn chưa biết, subdomain,
URL giả mạo, thiếu scheme, sai kiểu dữ liệu, credentials, IP, port lỗi,
whitespace/control, hostname lỗi và dispatch thật qua `ResearchAgent` với
fake provider. Toàn bộ unit test offline; fake provider không đo routing model.

Máy hiện tại: pytest 9.2 trên Python 3.10 lỗi nội bộ `_str_cache` trước khi
thu thập test. Đã chạy thành công bằng Python 3.13 có sẵn, dùng thư viện từ
`.venv`. Không sửa thư viện, requirements hay test của thành viên khác.

Lệnh PowerShell từ `starter_v0/` đã chạy:

```powershell
$env:PYTHONPATH = (Resolve-Path '.venv/Lib/site-packages').Path
& 'C:\Users\hi\AppData\Local\Programs\Python\Python313\python.exe' -m pytest -q --junitxml=runs/source_tire_pytest.xml
```

## Thử Agent thật

Provider/model: `openrouter`, `openai/gpt-4o-mini`, temperature 0.
Giả thuyết v2: chỉ thêm công cụ phân loại nguồn với điều kiện sử dụng rõ ràng
có thể route đúng yêu cầu mới và giữ các case base đã PASS.

Lệnh chạy bản cuối từ `starter_v0/`:

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v2-compact --suite base --eval-cases data/eval_base.json
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v2-compact --suite group --eval-cases data/eval_group.json
```

Đối chứng dùng `--tools artifacts/source_tire_control_tools_v1.yaml`:
10 declaration cũ giống nhau về dữ liệu YAML, cùng prompt v1. Hash file
đối chứng khác v1 do newline, không phải thay đổi nội dung declaration.
Snapshot mô tả dài ban đầu: `source_tire_initial_tools.yaml` (hash trùng run
v2 đầu tiên). Bản cuối chỉ rút gọn description của `source_tire`; không sửa
tool khác để điều chỉnh điểm.

## Kết quả đã đo

| Run | PASS | Mục đích |
|---|---:|---|
| v1 gốc | 16/20 | baseline đã có |
| v2 mô tả dài | 15/20 | thử declaration ban đầu |
| v2-repeat mô tả dài | 15/20 | kiểm tra lại regression R03 |
| v1-control | 16/20 | đối chứng không có tool mới |
| v2-compact bản cuối | **16/20** | rút gọn riêng description tool mới |
| v2-compact group | **5/5** | Agent route và thực thi tool mới |

Bản cuối giữ **đúng cả 16 case PASS của v1**, không có case PASS → FAIL.
Không có lời gọi `source_tire` thừa trong base eval.
So sánh từng case: [source_tire_comparison.json](source_tire_comparison.json).

Lần đầu R03 đổi `lookup.query` từ `AI` thành `AI news`, bị bộ chấm so args
đánh FAIL dù chọn đúng `lookup`. Sau khi rút gọn description mới, R03 PASS.
Đây là kết quả quan sát của các lượt chạy, không đảm bảo model luôn cho cùng
output ở mọi lần chạy kể cả temperature 0.

Bốn case FAIL còn lại vẫn là R08, R10, R12, R13 như v1. Metric
`tool_routing_accuracy` từ 0.85 ở v1 gốc xuống 0.80 ở bản cuối vì lựa chọn
tool trong R13 (case vốn đã FAIL) khác đi; đối chứng v1 chạy lại cũng là
0.80. `argument_accuracy` giữ 0.80, `multiturn_accuracy` giữ 1.00.
Không sửa lỗi cũ của các tool/prompt ngoài phạm vi yêu cầu.

Base eval đo routing/args, không bảo đảm các API tool cũ luôn trả nội dung
thành công. Với 5 case group mới đã kiểm tra cả `tool_results`: official/T1,
news/T2, social/T3, `invalid_url` và domain giả mạo → unknown/unrated đúng
quy tắc; không chỉ dựa vào điểm routing.

Log bản cuối:

- [Base 16/20](../runs/v2-compact_B_base_openrouter_20261110T113606053136.json)
- [Group 5/5](../runs/v2-compact_B_group_openrouter_20261110T113503629620.json)
- [Đối chứng 16/20](../runs/v1-control_B_base_openrouter_20261110T113435974364.json)

Các lần chạy đều được giữ trong `runs/` và ghi thêm vào `version_log.csv`,
bao gồm hai lần 15/20; không thay thế hay sửa log v0/v1 đã có.

## Đồng bộ với tool cite của nhóm

Sau khi các run trên hoàn tất, workspace nhận thêm `cite`, các case `G01`–`G10`
và test của nhóm. Đã bổ sung lại riêng import/registry/declaration `source_tire`
bên cạnh `cite`, giữ các nội dung mới của nhóm. 5 case `ST_` được thêm vào
group hiện tại; bản riêng `data/eval_source_tire.json` giúp chạy độc lập mà
không phải chạy các case nhóm khác.

Toàn suite sau đồng bộ: **126 PASS, 14 SKIP, 0 FAIL**, trong đó 49 test
`source_tire` PASS. Evidence: [JUnit sau đồng bộ](../runs/source_tire_merged_pytest.xml).
Số SKIP thay đổi vì nhóm đã bổ sung một số test cũ; không sửa các test đó.
Các run trước chỉ chứng minh cấu hình có hash ghi trong từng log. Khi cấu hình
chung đổi cần dùng run `v2-source-tire-merged` để đánh giá trạng thái mới.

Kết quả sau đồng bộ:

- [Base mới nhất: 20/20](../runs/v2-source-tire-merged_B_base_openrouter_20261110T114804379960.json), giữ đủ 16/16 case PASS v1.
- [Case riêng tool: 4/5](../runs/v2-source-tire-merged_B_group_openrouter_20261110T114656905887.json).
- [So sánh sau đồng bộ](source_tire_merged_comparison.json).

Case group chưa PASS là `ST_invalid`: URL `https://` khiến Agent dùng
`clarify` hỏi URL đầy đủ thay vì gọi `source_tire`. Hàm xử lý URL lỗi vẫn
PASS unit test. Giữ lại kết quả này, không sửa prompt hoặc tool khác để ép
đạt điểm. Mức tăng base lên 20/20 đi kèm prompt mới của nhóm và tool `cite`,
không quy kết là hiệu quả của riêng `source_tire`. Mục tiêu của phần việc này
chỉ là giữ 16 case PASS cũ, không tiếp tục tối ưu 4 case FAIL cũ.

Snapshot của cấu hình đã chạy: `source_tire_merged_tools.yaml` và
`source_tire_merged_system_prompt.md`; cả hai có hash trùng log sau đồng bộ.
Để chạy riêng 5 case của tool với cấu hình hiện tại, dùng
`--eval-cases data/eval_source_tire.json`.

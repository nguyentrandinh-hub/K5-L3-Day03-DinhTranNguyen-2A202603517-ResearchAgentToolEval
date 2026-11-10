# Sample formats (mock)

These are **mock examples** showing the *format* of the artifacts your team
submits — not real answers. Generate your own from real runs.

- `transcripts/example.transcript.json` — what `chat.py` writes per session.
- `run-analysis.csv` — what `scripts/parse_runs.py` produces from `runs/*.json`.
- `version_log.example.csv` — example layout for `artifacts/version_log.csv`.

Run logs (`runs/`) are not included; you produce those yourself.

## Research Desk UI

From `starter_v0/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).
Configure provider and research API keys in `.env` using `.env.example`.
The **All tools** tab lists every tool and its arguments, credential status,
and a JSON runner. Try `clean_results` without keys using its prefilled example.
**Research chat** supports multi-round retrieval, cleanup, and formatting with
visible tool traces. **Session log** downloads the full transcript; copies are
saved in `transcripts/`. Telegram actions require explicit approval in the UI.
Use locally for the lab; no authentication is provided for public hosting.

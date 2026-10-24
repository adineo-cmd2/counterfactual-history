# Counterfactual History Simulator — backend

Run from `backend/`:

```bash
pip install -r requirements.txt
cp .env.example .env   # optional; works with no keys (template engine)
python3 -m uvicorn app.main:app --port 8006
```

Tests: `python3 -m pytest tests/ -v` (5 tests).

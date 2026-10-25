# FastExpress API

Backend del módulo de cotización de envíos (FastAPI + PyTest).

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
pytest
```

- App: http://127.0.0.1:8000/
- Docs API: http://127.0.0.1:8000/docs

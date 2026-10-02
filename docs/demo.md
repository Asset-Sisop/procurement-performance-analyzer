# Demo Guide

## 1. Start the service

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## 2. Open the interface

Go to `http://127.0.0.1:8000` and select **Запустить тестовый сценарий**.

The UI shows:

- synthetic baseline;
- modelled optimization result;
- top bottleneck;
- operation timeline;
- optimization hypotheses.

## 3. Test the API

Use Swagger at `http://127.0.0.1:8000/docs` or send a `POST /api/analyze` request with a list of measured stages.

## 4. Interpretation

The demo is a proof of concept for the analytical workflow. The numbers are synthetic. They must not be presented as measured performance of a real procurement platform.

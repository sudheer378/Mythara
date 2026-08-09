# Mythara AI Studio

Personal AI creative operating system backend for lore ingestion, grounded Q&A, suggestions, draft generation, canon validation, Mythral encyclopedia persistence, and TTS audio file output.

## Run

```bash
pip install -e '.[test]'
uvicorn backend.app.main:app --reload
```

## Test

```bash
pytest
```

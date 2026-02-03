# SOP QA Service
SOP = Standard Operating Procedure  
QA = Question/Answer

## 1) Create conda env
```bash
conda create -n <env-name> python=3.11 -y
conda activate <env-name>
conda install -c conda-forge faiss-cpu -y
cd backend
pip install -r requirements.txt
```

### spaCy models (optional but recommended)
If you have them available:
```bash
python -m spacy download en_core_web_sm
python -m spacy download sv_core_news_sm
```
If you don't install models, the app will fall back to built-in stopword lists.

## 2) Put PDFs in `backend/data/pdfs/`
Example:
```
backend/data/pdfs/my_doc.pdf
```

## 3) Run API
```bash
cd backend
uvicorn app.main:app --reload
```

Open docs:
- http://127.0.0.1:8000/docs

## 4) Run backend tests
```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest
```
Run a specific test file:
```bash
python -m pytest tests/test_chunking.py
```
Run a single test function:
```bash
python -m pytest tests/test_chunking.py::test_chunk_pages_with_headings
```

## Main endpoints
- `POST /build`          build index for a PDF
- `POST /load`           load existing index from disk
- `POST /search`         semantic search (optional keyword filter)
- `POST /qa`             extractive answer using top passages
- `GET  /chunks/{id}`    retrieve full chunk content by chunk_id
- `GET  /health`         service status and readiness

## 5) Run frontend (Vite + React/TS)
```bash
cd frontend
npm install
npm run dev
```

Frontend dev server:
- http://127.0.0.1:5173

The frontend proxies `/api/*` to the backend at `http://127.0.0.1:8000`.

## 6) Run frontend tests
```bash
cd frontend
npm test
```

## Project layout
```
backend/         FastAPI service, tests, and data
frontend/        React + TypeScript frontend (Vite) with Vitest tests
```

## TODO
- Switch embeddings backend to OpenAI (update `model_name` in `backend/config.yaml` and replace `SentenceTransformer` in `backend/app/embeddings.py` and `backend/app/pipeline.py`).

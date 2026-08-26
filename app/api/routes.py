from pathlib import Path
import json

'''
    1) HTTPException  - used when we want to return an error response from the API routes
    2) CORSMiddleware - controls wheather browser are allowed to call the API from another origin 
       eg - frontend  - http://localhost:5173    backend - http://localhost:8001   
       those are different origins, so the browser checks CORS rules, this middle ware allows those frontend requests. 
    3) FileResponse   - sends a real file back to the browser
    4) StaticFiles    - serves a while folder of statis assets
'''
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import ARTIFACTS_DIR, FRONTEND_DIST_DIR, TOKENIZER_TYPES
from app.core.schemas import DecodeRequest, EncodeRequest, TrainRequest
from app.core.tokenizer_modules.basic import BasicTokenizer
from app.core.tokenizer_modules.regex_ import RegexTokenizer
from app.core.tokenizer_modules.base import get_stats, merge

tokenizer_store: dict = {
    "tokenizer" : None, 
    "type"      : None
}


def get_dataset_path(filename: str) -> Path:
    artifacts_dir = ARTIFACTS_DIR.resolve()
    path = (artifacts_dir/filename).resolve()       # combines the artifact folder with file name
    if path.parent != artifacts_dir or path.suffix != '.txt':      # making sure the file is directly inside the artifacts folder
        raise HTTPException(status_code=400, detail="Can accept only .txt file for now")
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Dataset not found")
    return path 


def stream_event(event_type: str, payload: dict) -> str:
    return json.dumps({"type": event_type, **payload}) + "\n"


def vocab_to_json(vocab: dict[int, bytes]) -> dict[str, str]:
    return {
        str(idx): token.decode("utf-8", errors="replace")
        for idx, token in vocab.items()
    }


def calculate_compression(tokenizer, text: str, tokenizer_type: str) -> dict:
    original_bytes = len(text.encode("utf-8"))
    if tokenizer_type == "basic":
        tokens, _ = tokenizer.encode(text)
    else:
        tokens, _, _ = tokenizer.encode_ordinary(text)
    token_count = len(tokens)
    ratio = round(original_bytes / token_count, 2) if token_count else 0
    return {
        "original_bytes": original_bytes,
        "token_count": token_count,
        "ratio": ratio,
    }


def train_basic_live(text: str, vocab_size: int):
    num_merges = vocab_size - 256
    ids = list(text.encode("utf-8"))
    vocab = {idx: bytes([idx]) for idx in range(256)}
    merges = {}

    yield stream_event("start", {"total": num_merges, "vocab": vocab_to_json(vocab)})

    for i in range(num_merges):
        stats = get_stats(ids)
        if not stats:
            break

        pair = max(stats, key=stats.get)
        idx = 256 + i
        ids = merge(ids, pair, idx)
        merges[pair] = idx
        vocab[idx] = vocab[pair[0]] + vocab[pair[1]]

        entry = {
            "step": i + 1,
            "total": num_merges,
            "pair": list(pair),
            "idx": idx,
            "token": vocab[idx].decode("utf-8", errors="replace"),
            "occurrences": stats[pair],
        }
        yield stream_event("merge", {"entry": entry, "vocab_entry": {str(idx): entry["token"]}})

    tokenizer = BasicTokenizer()
    tokenizer.merges = merges
    tokenizer.vocab = vocab
    return tokenizer


def train_regex_live(text: str, vocab_size: int):
    tokenizer = RegexTokenizer()
    num_merges = vocab_size - 256
    text_chunks = tokenizer.compiled_pattern.findall(text)
    ids = [list(chunk.encode("utf-8")) for chunk in text_chunks]
    vocab = {idx: bytes([idx]) for idx in range(256)}
    merges = {}

    yield stream_event("start", {"total": num_merges, "vocab": vocab_to_json(vocab)})

    for i in range(num_merges):
        stats = {}
        for chunk_ids in ids:
            get_stats(chunk_ids, stats)

        if not stats:
            break

        pair = max(stats, key=stats.get)
        idx = 256 + i
        ids = [merge(chunk_ids, pair, idx) for chunk_ids in ids]
        merges[pair] = idx
        vocab[idx] = vocab[pair[0]] + vocab[pair[1]]

        entry = {
            "step": i + 1,
            "total": num_merges,
            "pair": list(pair),
            "idx": idx,
            "token": vocab[idx].decode("utf-8", errors="replace"),
            "occurrences": stats[pair],
        }
        yield stream_event("merge", {"entry": entry, "vocab_entry": {str(idx): entry["token"]}})

    tokenizer.merges = merges
    tokenizer.vocab = vocab
    return tokenizer


def create_app() -> FastAPI:
    app = FastAPI(title="BPE Tokenizer")      # creating the actual web application object
                                              # this is where all the routes like /api/train ... get registered
    app.add_middleware(
        CORSMiddleware,                       # handles browser security rules for cross-origin request
        allow_origins=['*'],                  # allow request from any website/origin. 
        allow_methods=['*'],                  # allow all HTTP methods
        allow_headers=['*'],                  # allow all request headers
    )
    register_api_routes(app)
    register_frontend_routes(app)
    return app

def register_api_routes(app: FastAPI) -> None:
    @app.get('/api/datasets')
    def list_datasets():
        if not ARTIFACTS_DIR.exists():
            return {"datasets" : []}
        files = [f.name for f in ARTIFACTS_DIR.iterdir() if f.suffix == '.txt']
        return {'datasets' : files}

    @app.get('/api/datasets/{filename}')
    def get_dataset_preview(filename: str, chars: int = 500):
        path = get_dataset_path(filename)
        text = path.read_text(encoding='utf-8')
        return {
            'filename'    : filename,
            'total_chars' : len(text),
            'total_bytes' : len(text.encode('utf-8')),
            'preview'     : text[:chars],
        }

    @app.post('/api/train')
    def train(req:TrainRequest):
        path = get_dataset_path(req.dataset)
        if req.vocab_size < 256:
            raise HTTPException(status_code=400, detail="Vocab_size must be >= 256")

        if req.tokenizer_type not in TOKENIZER_TYPES:
            raise HTTPException(status_code=400, detail="token_type must be basic or regex")

        text = path.read_text(encoding='utf-8')
        if not text:
            raise HTTPException(status_code=400, detail='Dataset is empty')

        if req.tokenizer_type == "basic":
            tokenizer = BasicTokenizer()
        else:
            tokenizer = RegexTokenizer()

        merge_log = tokenizer.train(text, vocab_size=req.vocab_size, verbose=False)
        tokenizer_store['tokenizer'] = tokenizer
        tokenizer_store['type'] = req.tokenizer_type

        vocab = {
            str(idx) : token.decode('utf-8', errors='replace')
            for idx, token in tokenizer.vocab.items()
        }

        original_bytes = len(text.encode('utf-8'))
        if req.tokenizer_type == 'basic':
            tokens, _ = tokenizer.encode(text)
        else:
            tokens, _, _ = tokenizer.encode_ordinary(text)
        token_count = len(tokens)
        ratio = round(original_bytes/ token_count, 2) if token_count else 0

        return {
            'merge_log'           : merge_log,
            'vocab'               : vocab,
            'compression' : {
                'original_bytes'  : original_bytes,
                'token_count'     : token_count,
                'ratio'           : ratio
            },
        }

    @app.post('/api/train/stream')
    def train_stream(req: TrainRequest):
        path = get_dataset_path(req.dataset)
        if req.vocab_size < 256:
            raise HTTPException(status_code=400, detail="Vocab_size must be >= 256")

        if req.tokenizer_type not in TOKENIZER_TYPES:
            raise HTTPException(status_code=400, detail="token_type must be basic or regex")

        text = path.read_text(encoding='utf-8')
        if not text:
            raise HTTPException(status_code=400, detail='Dataset is empty')

        def events():
            if req.tokenizer_type == "basic":
                tokenizer = yield from train_basic_live(text, req.vocab_size)
            else:
                tokenizer = yield from train_regex_live(text, req.vocab_size)

            tokenizer_store['tokenizer'] = tokenizer
            tokenizer_store['type'] = req.tokenizer_type
            compression = calculate_compression(tokenizer, text, req.tokenizer_type)
            yield stream_event("done", {
                "vocab": vocab_to_json(tokenizer.vocab),
                "compression": compression,
            })

        return StreamingResponse(events(), media_type="application/x-ndjson")

    @app.post('/api/encode')
    def encode(req: EncodeRequest):
        tokenizer = tokenizer_store['tokenizer']
        if tokenizer is None: 
            raise HTTPException(status_code=400, detail="Tokenizer not trained yet")
        
        original_bytes = list(req.text.encode('utf-8'))

        if tokenizer_store['type'] == 'basic':
            ids, encode_log = tokenizer.encode(req.text)
            chunks = []
        else:
            ids, encode_log, chunks = tokenizer.encode(req.text, allowed_special=req.allowed_special)

        return {
            'text'                : req.text,
            'original_bytes'      : original_bytes,
            'ids'                 : ids,
            'encode_log'          : encode_log,
            'chunks'              : chunks, 
            'original_byte_count' : len(original_bytes),
            'token_count'         : len(ids),
        }

    @app.post('/api/decode')
    def decode(req:DecodeRequest):
        tokenizer = tokenizer_store['tokenizer']
        if tokenizer is None:
            raise HTTPException(status_code=400, detail="Tokenizer not trained yet")
        try:
            text = tokenizer.decode(req.ids)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {'text' : text}

    @app.get('/api/health')
    def health():
        return {
            'status'              : 'ok',
            'tokenizer_trained'   : tokenizer_store['tokenizer'] is not None,
            'tokenizer_type'      : tokenizer_store['type']
        }

def register_frontend_routes(app: FastAPI) -> None:
    if FRONTEND_DIST_DIR.exists():
        assets_dir = FRONTEND_DIST_DIR / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get('/{full_path:path}')
    def serve_frontend(full_path: str):
        request_path = FRONTEND_DIST_DIR / full_path
        if request_path.is_file():
            return FileResponse(request_path)

        index_path = FRONTEND_DIST_DIR / 'index.html'
        if index_path.exists():
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Front end build not found . Run 'npm run build' in fronend")

# app = create_app()
    


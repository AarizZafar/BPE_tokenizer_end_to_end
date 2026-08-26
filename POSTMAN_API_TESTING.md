# Postman API Testing Guide

Base URL:

```text
http://127.0.0.1:8001
```

Start the server before testing:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.api.routes:app --host 127.0.0.1 --port 8001 --reload
```

For every `POST` request in Postman:

```text
Body -> raw -> JSON
```

Use this header:

```text
Content-Type: application/json
```

Important: run `/api/train` before `/api/encode` or `/api/decode`. The tokenizer is stored in memory, so restarting the server clears it.

## 1. Health Check

Method:

```text
GET
```

URL:

```text
http://127.0.0.1:8001/api/health
```

Body:

```text
No body
```

Expected output before training:

```json
{
  "status": "ok",
  "tokenizer_trained": false,
  "tokenizer_type": null
}
```

Expected output after training:

```json
{
  "status": "ok",
  "tokenizer_trained": true,
  "tokenizer_type": "regex"
}
```

## 2. List Datasets

Method:

```text
GET
```

URL:

```text
http://127.0.0.1:8001/api/datasets
```

Body:

```text
No body
```

Expected output:

```json
{
  "datasets": [
    "law_of_human_nature.txt"
  ]
}
```

## 3. Dataset Preview

Method:

```text
GET
```

URL:

```text
http://127.0.0.1:8001/api/datasets/law_of_human_nature.txt?chars=500
```

Body:

```text
No body
```

Expected output:

```json
{
  "filename": "law_of_human_nature.txt",
  "total_chars": 12345,
  "total_bytes": 12345,
  "preview": "First 500 characters of the dataset..."
}
```

Common errors:

```json
{
  "detail": "Dataset not found"
}
```

```json
{
  "detail": "Can accept only .txt file for now"
}
```

## 4. Train Tokenizer

Method:

```text
POST
```

URL:

```text
http://127.0.0.1:8001/api/train
```

Raw JSON body:

```json
{
  "dataset": "law_of_human_nature.txt",
  "vocab_size": 276,
  "tokenizer_type": "regex"
}
```

You can also test the basic tokenizer:

```json
{
  "dataset": "law_of_human_nature.txt",
  "vocab_size": 276,
  "tokenizer_type": "basic"
}
```

Expected output shape:

```json
{
  "merge_log": [
    {
      "step": 1,
      "total": 20,
      "pair": [32, 116],
      "idx": 256,
      "token": " t",
      "occurrences": 100
    }
  ],
  "vocab": {
    "0": "\u0000",
    "1": "\u0001",
    "2": "\u0002",
    "256": " t"
  },
  "compression": {
    "original_bytes": 12345,
    "token_count": 9876,
    "ratio": 1.25
  }
}
```

Notes:

```text
merge_log length = vocab_size - 256, unless the dataset runs out of mergeable pairs.
```

Common errors:

```json
{
  "detail": "Dataset is empty"
}
```

```json
{
  "detail": "Vocab_size must be >= 256"
}
```

```json
{
  "detail": "token_type must be basic or regex"
}
```

## 5. Encode Text

Run `/api/train` successfully first.

Method:

```text
POST
```

URL:

```text
http://127.0.0.1:8001/api/encode
```

Raw JSON body:

```json
{
  "text": "hello world",
  "allowed_special": "all"
}
```

Expected output shape:

```json
{
  "text": "hello world",
  "original_bytes": [104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100],
  "ids": [104, 101, 108, 108, 111, 256, 119, 111, 114, 108, 100],
  "encode_log": [
    {
      "pair": [32, 119],
      "idx": 256
    }
  ],
  "chunks": [
    {
      "chunk": "hello",
      "bytes": [104, 101, 108, 108, 111],
      "ids": [104, 101, 108, 108, 111]
    }
  ],
  "original_byte_count": 11,
  "token_count": 10
}
```

Common error:

```json
{
  "detail": "Tokenizer not trained yet"
}
```

If you see that, run `/api/train` again. Server restarts clear the tokenizer.

## 6. Decode IDs

Run `/api/train` successfully first.

Method:

```text
POST
```

URL:

```text
http://127.0.0.1:8001/api/decode
```

Raw JSON body:

```json
{
  "ids": [104, 101, 108, 108, 111]
}
```

Expected output:

```json
{
  "text": "hello"
}
```

Common error:

```json
{
  "detail": "Tokenizer not trained yet"
}
```

Invalid token error example:

```json
{
  "detail": "invalid token id: 999999"
}
```

## Recommended Test Order

1. `GET /api/health`
2. `GET /api/datasets`
3. `GET /api/datasets/law_of_human_nature.txt?chars=500`
4. `POST /api/train`
5. `GET /api/health`
6. `POST /api/encode`
7. `POST /api/decode`


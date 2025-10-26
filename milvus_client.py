# app/milvus_client.py
# ------------------------------------------------------------
# 이 파일이 하는 일(요약)
# - Milvus Standard(서버형)에 접속해서 컬렉션 생성 + 업서트
# ------------------------------------------------------------
from typing import List
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
from app.config import MILVUS_URI, MILVUS_USER, MILVUS_PASS, MILVUS_DB, MILVUS_COL, EMBED_DIM

def _connect():
    # 이 코드가 뜻하는 바: 서버형 Milvus에 접속한다.
    connections.connect(
        alias="default",
        uri=MILVUS_URI,
        user=MILVUS_USER or None,
        password=MILVUS_PASS or None,
        db_name=MILVUS_DB or "default",
    )

def _ensure_collection() -> Collection:
    # 이 코드가 뜻하는 바: 컬렉션 없으면 만들고 인덱스를 생성한다.
    if not utility.has_collection(MILVUS_COL):
        fields = [
            FieldSchema(name="chunk_uid", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBED_DIM),
            FieldSchema(name="path", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="chunk_idx", dtype=DataType.INT64),
            FieldSchema(name="lang", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="chunk_hash", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="chunk_commit_sha", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="line_start", dtype=DataType.INT64),
            FieldSchema(name="line_end", dtype=DataType.INT64),
        ]
        schema = CollectionSchema(fields=fields, description="code chunks")
        col = Collection(name=MILVUS_COL, schema=schema)
        col.create_index(
            field_name="embedding",
            index_params={"index_type": "HNSW", "metric_type": "COSINE", "params": {"M": 24, "efConstruction": 200}},
        )
        col.load()
        return col
    col = Collection(MILVUS_COL)
    col.load()
    return col

def upsert_chunks(uids: List[str], vecs, metas: List[dict]) -> int:
    # 이 코드가 뜻하는 바: 같은 uid는 삭제 후 insert로 간단 업서트.
    _connect()
    col = _ensure_collection()
    if not uids:
        return 0

    expr = "chunk_uid in [" + ",".join(f'"{u}"' for u in uids) + "]"
    try:
        col.delete(expr)
    except Exception:
        pass

    entities = [
        uids,
        vecs,
        [m["path"] for m in metas],
        [int(m["chunk_idx"]) for m in metas],
        [str(m["lang"]) for m in metas],
        [str(m["chunk_hash"]) for m in metas],
        [str(m.get("chunk_commit_sha") or "") for m in metas],
        [int(m["line_start"]) for m in metas],
        [int(m["line_end"]) for m in metas],
    ]
    mr = col.insert(entities)
    col.flush()
    return len(mr.primary_keys)

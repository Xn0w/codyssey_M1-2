"""
firestore_service.py
---------------------
Firestore와 실제로 대화하는 코드는 전부 여기 모아둔다.
라우터(routers/)는 "무엇을 할지"만 알고, "어떻게 저장하는지"는 이 파일이 담당한다.
이렇게 나눠두면 나중에 DB를 바꾸더라도 라우터 코드는 거의 건드릴 필요가 없다.
"""

import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

from config import FIREBASE_CREDENTIALS_PATH, FIREBASE_CREDENTIALS_JSON

# Firebase 앱은 프로세스 전체에서 딱 한 번만 초기화해야 한다.
# (안 그러면 "app already exists" 에러가 난다)
if not firebase_admin._apps:
    if FIREBASE_CREDENTIALS_JSON:
        # 배포 환경(Render 등): 환경변수에 통째로 넣어둔 JSON 문자열을 파싱해서 사용
        cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON)
        cred = credentials.Certificate(cred_dict)
    else:
        # 로컬 개발 환경: firebase-key.json 파일을 그대로 사용
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

DATA_COLLECTION = "data"
CONVERSATIONS_COLLECTION = "conversations"


# ============ data 컬렉션 CRUD ============

def create_data_item(item: dict) -> dict:
    """데이터 1건을 추가하고, 생성된 id를 포함해서 돌려준다."""
    item["created_at"] = datetime.now(timezone.utc).isoformat()
    doc_ref = db.collection(DATA_COLLECTION).document()
    doc_ref.set(item)
    return {"id": doc_ref.id, **item}


def list_data_items() -> list[dict]:
    """전체 데이터 목록을 날짜순으로 정렬해서 반환."""
    docs = db.collection(DATA_COLLECTION).order_by("date").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

def get_data_in_range(start_date: str, end_date: str) -> list[dict]:
    """
    특정 기간(start_date ~ end_date)의 데이터만 조회.
    AI가 "특정 날짜/기간의 상세 데이터"가 필요하다고 판단했을 때
    Function Calling(도구 호출)으로 이 함수를 실행한다.
    """
    docs = (
        db.collection(DATA_COLLECTION)
        .where("date", ">=", start_date)
        .where("date", "<=", end_date)
        .order_by("date")
        .stream()
    )
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def update_data_item(item_id: str, updates: dict) -> dict:
    """None이 아닌 필드만 골라서 부분 수정."""
    updates = {k: v for k, v in updates.items() if v is not None}
    doc_ref = db.collection(DATA_COLLECTION).document(item_id)
    doc_ref.update(updates)
    updated_doc = doc_ref.get()
    return {"id": updated_doc.id, **updated_doc.to_dict()}


def delete_data_item(item_id: str) -> None:
    db.collection(DATA_COLLECTION).document(item_id).delete()


# ============ conversations 컬렉션 CRUD ============

def create_conversation(title: str) -> dict:
    conv = {
        "title": title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
    }
    doc_ref = db.collection(CONVERSATIONS_COLLECTION).document()
    doc_ref.set(conv)
    return {"id": doc_ref.id, **conv}


def list_conversations() -> list[dict]:
    """목록 조회에서는 messages는 빼고 제목/날짜만 가볍게 반환한다."""
    docs = db.collection(CONVERSATIONS_COLLECTION).order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).stream()
    result = []
    for doc in docs:
        data = doc.to_dict()
        result.append({
            "id": doc.id,
            "title": data.get("title"),
            "created_at": data.get("created_at"),
        })
    return result


def get_conversation(conversation_id: str) -> dict | None:
    """단건 조회에서는 messages를 전부 포함해서 반환한다."""
    doc = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def append_message(conversation_id: str, role: str, content: str) -> None:
    """대화 문서의 messages 배열에 메시지 1개를 추가한다."""
    doc_ref = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id)
    doc_ref.update({
        "messages": firestore.ArrayUnion([{
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }])
    })


def delete_conversation(conversation_id: str) -> None:
    db.collection(CONVERSATIONS_COLLECTION).document(conversation_id).delete()

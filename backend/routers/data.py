"""
routers/data.py
----------------
'/api/data' 관련 엔드포인트. 라우터는 얇게 유지하고
실제 로직은 services/ 쪽에 위임한다 (Controller는 가볍게, Service는 무겁게).
"""

from fastapi import APIRouter, HTTPException

from models.schemas import DataItem, DataItemUpdate, DataItemResponse
from services import firestore_service, summary_service

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("", response_model=DataItemResponse)
def add_data(item: DataItem):
    created = firestore_service.create_data_item(item.model_dump())
    return created


@router.get("", response_model=list[DataItemResponse])
def get_data_list():
    return firestore_service.list_data_items()


@router.put("/{item_id}", response_model=DataItemResponse)
def update_data(item_id: str, item: DataItemUpdate):
    updated = firestore_service.update_data_item(item_id, item.model_dump())
    return updated


@router.delete("/{item_id}")
def delete_data(item_id: str):
    firestore_service.delete_data_item(item_id)
    return {"message": "삭제되었습니다.", "id": item_id}


# summary는 /api/data/{item_id} 보다 먼저 선언해야
# FastAPI가 "summary"를 item_id로 착각하지 않는다 (경로 순서 주의!)
@router.get("/summary")
def get_data_summary():
    items = firestore_service.list_data_items()
    return summary_service.calculate_summary(items)

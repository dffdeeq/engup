from fastapi import APIRouter, Depends

from src.api.depends import get_metrics_repo
from src.api.metrics.schemas import MetricsData
from src.repos.factories.metrics_data import MetricsDataRepo

router = APIRouter()


@router.post("/save_metrics")
async def save_metrics(data: MetricsData, metrics_repo: MetricsDataRepo = Depends(get_metrics_repo)):
    await metrics_repo.create_metrics_data(data.uuid, data.metrics_string)

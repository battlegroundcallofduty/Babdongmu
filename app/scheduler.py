"""애플리케이션 스케줄러."""

import asyncio
import logging

from app.config import settings
from app.database import AsyncSessionLocal
from app.domain.hosting.service import run_hosting_status_scheduler

logger = logging.getLogger(__name__)


async def hosting_scheduler_loop() -> None:
    """호스팅 상태 스케줄러를 주기적으로 실행합니다."""

    logger.info(
        "호스팅 상태 스케줄러를 시작합니다. interval_seconds=%s",
        settings.SCHEDULER_INTERVAL_SECONDS,
    )

    try:
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    changed_count = await run_hosting_status_scheduler(session=session)

                    if changed_count > 0:
                        logger.info(
                            "호스팅 상태 스케줄러 처리 완료: changed_count=%s",
                            changed_count,
                        )

            except Exception:
                logger.exception("호스팅 상태 스케줄러 실행 중 오류가 발생했습니다.")

            await asyncio.sleep(settings.SCHEDULER_INTERVAL_SECONDS)

    except asyncio.CancelledError:
        logger.info("호스팅 상태 스케줄러를 종료합니다.")
        raise

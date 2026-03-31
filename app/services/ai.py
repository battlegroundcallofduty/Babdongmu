"""AI 요약 생성 서비스 (OpenAI 기반)."""

from app.config import settings


SUMMARY_PROMPT = """당신은 독거 어르신을 위한 식사 동반 플랫폼 '밥동무'의 AI 어시스턴트입니다.
봉사자들이 남긴 후기를 바탕으로, 어르신의 매력을 자연스럽게 소개하는 짧은 문구를 생성하세요.

규칙:
- 2~3문장, 따뜻하고 친근한 톤
- 어르신의 음식 솜씨, 성격, 분위기 등 긍정적 특성 중심
- 봉사자가 다시 방문하고 싶게 만드는 문구
- 개인정보(주소, 연락처 등)는 절대 포함하지 않을 것

후기 목록:
{reviews}

소개 문구:"""


async def generate_senior_summary(reviews: list[str]) -> str:
    """후기 목록을 받아 어르신 AI 소개글을 생성합니다."""
    # TODO: OpenAI API 호출 구현
    # 1. reviews가 최소 3개 이상일 때만 생성
    # 2. SUMMARY_PROMPT에 후기를 삽입하여 LLM 호출
    # 3. 생성된 요약을 반환
    pass


async def update_senior_ai_summary(senior_id: str) -> str | None:
    """어르신의 후기를 조회하고 AI 요약을 갱신합니다."""
    # TODO: 구현 순서
    # 1. senior_id로 해당 어르신의 후기 목록 조회
    # 2. 후기가 충분하면 generate_senior_summary 호출
    # 3. seniors 컬렉션의 ai_summary, ai_summary_updated_at 업데이트
    # 4. 생성된 요약 반환
    pass

"""유저 MongoDB 문서 스키마."""


def user_document(
    email: str,
    hashed_password: str,
    name: str,
    phone: str,
    role: str,
    district: str,
) -> dict:
    """유저 문서를 생성합니다.

    Args:
        role: "volunteer" | "guardian" | "admin"
        district: 행정동 (예: "서울시 성북구 정릉동")
    """
    return {
        "email": email,
        "hashed_password": hashed_password,
        "name": name,
        "phone": phone,
        "role": role,
        "district": district,
        "verification_status": "unverified",  # unverified -> verified
        "total_hours": 0.0,
        "visit_count": 0,
        "is_active": True,
    }

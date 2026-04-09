# 밥동무 데이터베이스 설계

## 기술 스택
- **DB**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.x (asyncio / Mapped 스타일)
- **드라이버**: asyncpg
- **마이그레이션**: Alembic

---

## 테이블 목록

| 테이블 | 설명 | ORM 모델 위치 |
|--------|------|---------------|
| `users` | 회원 (봉사자 / 보호자 / 관리자) | `app/domain/user/models.py` → `User` |
| `documents` | 봉사자 신원 서류 | `app/domain/user/models.py` → `Document` |
| `seniors` | 어르신 정보 | `app/domain/senior/models.py` → `Senior` |
| `hostings` | 호스팅 (어르신이 개설하는 밥자리) | `app/domain/hosting/models.py` → `Hosting` |
| `matching_info` | 매칭 신청 정보 | `app/domain/match/models.py` → `MatchingInfo` |
| `reviews` | 후기 | `app/domain/review/models.py` → `Review` |
| `review_img` | 후기 이미지 (최대 5개) | `app/domain/review/models.py` → `ReviewImg` |
| `sms_logs` | SMS 발송 이력 | `app/domain/hosting/models.py` → `SmsLog` |

---

## 테이블 상세

### users
| 컬럼 | 타입 | 설명 |
|------|------|------|
| user_id | PK | 회원 ID |
| name | VARCHAR | 이름 |
| email | VARCHAR | 이메일 |
| password | VARCHAR | 비밀번호 해시 |
| phone_number | VARCHAR | 전화번호 |
| address | VARCHAR | 주소 |
| user_role | VARCHAR | 역할 (`volunteer` / `guardian` / `admin`) |
| cert_flag | VARCHAR | 인증 여부 (`pending` / `approved` / `rejected`) |
| created_at | TIMESTAMP | 가입일 |
| updated_at | TIMESTAMP | 수정일 |

---

### documents
| 컬럼 | 타입 | 설명 |
|------|------|------|
| document_id | PK | 서류 ID |
| user_id | FK → users | 회원 |
| document_url | VARCHAR | 서류 파일 URL |
| document_type | VARCHAR | 서류 타입 |
| created_at | TIMESTAMP | 등록일 |
| updated_at | TIMESTAMP | 수정일 |

> 서류 심사 결과는 `users.cert_flag`로 관리

---

### seniors
| 컬럼 | 타입 | 설명 |
|------|------|------|
| senior_id | PK | 어르신 ID |
| guardian_id | FK → users | 담당 보호자 |
| name | VARCHAR | 이름 |
| gender | VARCHAR | 성별 |
| age | INT | 나이 |
| address | VARCHAR | 주소 |
| special_note | TEXT | 특이사항 (병력, 주의사항) |
| active_flag | BOOLEAN | 활성 상태 |
| ai_summary | TEXT | Gemini AI 생성 소개글 |
| max_people | INT | 수용 가능 인원 (호스팅 기본값으로 사용) |
| qr_code | VARCHAR | QR 코드 이미지 URL (senior_id 기반 생성 후 저장) |
| created_at | TIMESTAMP | 등록일 |

---

### hostings
| 컬럼 | 타입 | 설명 |
|------|------|------|
| hosting_id | PK | 호스팅 ID |
| senior_id | FK → seniors | 어르신 |
| menu | VARCHAR | 메뉴 |
| hosting_at | TIMESTAMP | 호스팅 시작 일시 |
| hosting_end | TIMESTAMP | 호스팅 종료 일시 |
| max_people | INT | 모집 가능 인원 (seniors.max_people이 기본값, 수정 가능) |
| hosting_status | VARCHAR | 모집 상태 (`신청가능` / `모집완료` / `신청불가`) |
| created_at | TIMESTAMP | 생성일 |
| updated_at | TIMESTAMP | 수정일 |
| visited_at | TIMESTAMP | 방문일 |

> 기존 `hosting_time` 단일 컬럼을 `hosting_at`(시작) / `hosting_end`(종료) 두 컬럼으로 분리

---

### matching_info
| 컬럼 | 타입 | 설명 |
|------|------|------|
| matching_id | PK | 매칭 ID |
| hosting_id | FK → hostings | 호스팅 |
| vt_id | FK → users | 봉사자 |
| is_apply | BOOLEAN | 신청/취소 여부 |
| check_in | BOOLEAN | 방문 체크인 여부 |
| check_in_time | TIMESTAMP | 체크인 시간 |
| check_out_time | TIMESTAMP | 체크아웃 시간 |
| actual_volunteer_time | INT | 실봉사시간 (이 호스팅에서 실 부여되는 시간, 분 단위) |
| created_at | TIMESTAMP | 신청일 |

---

### reviews
| 컬럼 | 타입 | 설명 |
|------|------|------|
| review_id | PK | 후기 ID |
| matching_id | FK → matching_info | 매칭 정보 |
| vt_id | FK → users | 봉사자 |
| contents | TEXT | 후기 내용 |
| created_at | TIMESTAMP | 작성일 |
| updated_at | TIMESTAMP | 수정일 |

---

### review_img
| 컬럼 | 타입 | 설명 |
|------|------|------|
| image_id | PK | 이미지 ID |
| review_id | FK → reviews | 후기 |
| image_url | VARCHAR | 이미지 URL |
| created_at | TIMESTAMP | 등록일 |

> 후기당 최대 5개

---

### sms_logs
| 컬럼 | 타입 | 설명 |
|------|------|------|
| sms_id | PK | SMS ID |
| hosting_id | FK → hostings | 관련 호스팅 |
| receiver_id | FK → users | 수신자 |
| is_send | BOOLEAN | 발송 성공 여부 |
| alarm_type | VARCHAR | 알람 구분 (`match` / `checkin` / `checkout` / `update`) |
| contents | TEXT | 발송 내용 |
| created_at | TIMESTAMP | 발송일 |

> 수신자가 여러 명인 경우 수신자별로 row 생성 (예: 호스팅 수정 시 신청한 봉사자 전원)

---

## SMS 발송 트리거

| alarm_type | 발송 시점 | 수신자 |
|------------|-----------|--------|
| `match` | 봉사자가 호스팅 신청 시 | 보호자 |
| `checkin` | 봉사자가 방문 체크인 시 | 보호자 |
| `checkout` | 봉사자가 방문 체크아웃 시 | 보호자 |
| `update` | 호스팅 정보 수정 시 | 신청한 봉사자 전원 |

---

## 테이블 관계 요약

```
users ──< documents
users ──< seniors (보호자)
seniors ──< hostings
hostings ──< matching_info
users ──< matching_info (봉사자)
matching_info ──< reviews
users ──< reviews (봉사자)
reviews ──< review_img
hostings ──< sms_logs
users ──< sms_logs (수신자)
```

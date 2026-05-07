/**
 * format-utils.js
 * 여러 파일에서 공통으로 사용하는 포맷·파싱·검증 유틸 모음
 *
 * 포함 항목:
 *   - KST_TIME_ZONE    : 한국 타임존 상수 (Asia/Seoul 하드코딩 방지)
 *   - parseApiDateTime : API 응답 ISO 날짜 문자열 → Date 객체 파싱
 *                        (타임존 정보 없는 문자열은 UTC로 정규화)
 *   - normalizePhone   : 전화번호 정규화 및 유효성 검증 (010+8자리)
 *
 * 날짜 표시 형식 함수(formatDate, formatTime 등)는 각 파일마다
 * 원하는 출력 형식이 달라 공통화하지 않고 각 파일에 그대로 둠.
 */

export const KST_TIME_ZONE = 'Asia/Seoul';

// API 날짜 문자열을 Date 객체로 변환
// 타임존 정보(Z, +09:00)가 없는 ISO 문자열은 UTC로 간주해 정규화
export function parseApiDateTime(value) {
  if (!value) {
    return null;
  }

  if (value instanceof Date) {
    return value;
  }

  if (typeof value === 'string') {
    const normalizedValue = value.includes('T')
      && !value.endsWith('Z')
      && !/[+-]\d{2}:\d{2}$/.test(value)
      ? `${value}Z`
      : value;

    return new Date(normalizedValue);
  }

  return new Date(value);
}

// 하이픈·공백 제거 후 010+8자리 검증, 유효하지 않은 형식은 null
export function normalizePhone(raw) {
  const digits = raw.trim().replace(/[-\s]/g, '');
  return /^010\d{8}$/.test(digits) ? digits : null;
}

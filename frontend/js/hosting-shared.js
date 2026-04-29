/**
 * hosting-shared.js
 * 호스팅 관련 공통 헬퍼 + 공통 스타일
 * 사용 페이지: hosting-match.html, hostings.html
 *
 * 이 모듈을 import 하면 자동으로 공통 CSS가 <head>에 주입됩니다.
 * (별도의 <link rel="stylesheet"> 추가가 필요 없음)
 */

/* ================================================================
 * 0. 공통 CSS 자동 주입
 *    - 모듈은 한 번만 평가되므로 중복 주입은 일어나지 않지만,
 *      안전하게 id 가드로 한 번 더 막아둠
 * ================================================================ */

const SHARED_STYLE_ID = 'hosting-shared-styles';

const SHARED_CSS = `
.hidden { display: none !important; }

/* ---------- 필터 바 ---------- */
.filter-bar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

/* ---------- 호스팅 카드 ---------- */
.hosting-card {
  display: block;
  text-decoration: none;
  color: inherit;
  height: 100%;
  cursor: pointer;
}

.hosting-card .card-body {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.hosting-card:focus-visible {
  outline: 3px solid rgba(212, 118, 60, 0.35);
  outline-offset: 4px;
}

.hosting-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.hosting-avatar {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #D4763C, #5B8C5A);
  flex-shrink: 0;
}

.hosting-header-text {
  min-width: 0;
  flex: 1;
}

.hosting-name {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.45;
  color: #2C2420;
  margin-bottom: 6px;
  word-break: keep-all;
}

.hosting-address {
  color: #8C7E73;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  word-break: keep-all;
}

.hosting-menu {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.4;
  color: #D4763C;
  margin-bottom: 16px;
  word-break: keep-all;
}

.hosting-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hosting-status-row-after-menu {
  margin-bottom: 14px;
}

.hosting-status-badge {
  width: fit-content;
}

.hosting-meta {
  display: block;
  margin-bottom: 12px;
  padding-top: 14px;
  border-top: 1px solid #F2ECE6;
}

.hosting-meta-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  min-width: 0;
  color: #6B5E53;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
}

.hosting-meta-row + .hosting-meta-row {
  margin-top: 6px;
}

.hosting-meta-label {
  min-width: 36px;
  color: #8C7E73;
  font-weight: 700;
  flex-shrink: 0;
}

.hosting-meta-value {
  min-width: 0;
  word-break: keep-all;
}

.hosting-helper {
  color: #8C7E73;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  margin-bottom: 16px;
}

.hosting-card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: auto;
}

.hosting-card-actions .btn {
  flex: 1;
  min-width: 0;
}

/* ---------- 배지 ---------- */
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}

.badge-open { background: #EDF5ED; color: #3A6B39; }
.badge-full { background: #FDF5E6; color: #8B6914; }
.badge-failed { background: #FDECEC; color: #B44646; }
.badge-progress { background: #EEF3FF; color: #4269B4; }
.badge-closed { background: #F0EBE6; color: #6B5E53; }
.badge-my-applied { background: #F3EDF8; color: #6D4A8A; }

/* ---------- 빈 상태 ---------- */
.empty-state {
  padding: 56px 24px;
  text-align: center;
}

.empty-state-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  color: #D4763C;
}

/* ---------- 알림 모달 (info / success / error) ---------- */
.alert-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: none;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 60;
  box-sizing: border-box;
}

.alert-modal-overlay.open {
  display: flex;
}

.alert-modal {
  width: min(100%, 420px);
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 48px rgba(44, 36, 32, 0.18);
  padding: 24px;
}

.alert-modal-title {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.4;
  color: #2C2420;
  margin-bottom: 8px;
}

.alert-modal-message {
  font-size: 15px;
  line-height: 1.6;
  color: #6B5E53;
  margin-bottom: 20px;
  white-space: pre-wrap;
  word-break: keep-all;
}

.alert-modal-actions {
  display: flex;
  justify-content: flex-end;
}

.alert-modal.success .alert-modal-title { color: #2E5D2E; }
.alert-modal.error .alert-modal-title { color: #9A3838; }
.alert-modal.info .alert-modal-title { color: #6B5E53; }

body.modal-open {
  overflow: hidden;
}

/* ---------- 반응형 ---------- */
@media (max-width: 768px) {
  .filter-bar {
    grid-template-columns: 1fr;
  }

  .hosting-card-actions .btn {
    width: 100%;
  }

  .hosting-name {
    font-size: 17px;
  }

  .hosting-menu {
    font-size: 20px;
  }

  .alert-modal {
    padding: 20px;
  }
}
`;

function injectSharedStyles() {
  // 비-브라우저 환경 가드 (테스트 등)
  if (typeof document === 'undefined') {
    return;
  }
  if (document.getElementById(SHARED_STYLE_ID)) {
    return;
  }
  const styleElement = document.createElement('style');
  styleElement.id = SHARED_STYLE_ID;
  styleElement.textContent = SHARED_CSS;
  document.head.appendChild(styleElement);
}

injectSharedStyles();

/* ================================================================
 * 1. 상수
 * ================================================================ */

export const KST_TIME_ZONE = 'Asia/Seoul';

/* ================================================================
 * 2. 문자열 / 날짜 유틸
 * ================================================================ */

export function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

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

/* ================================================================
 * 4. 호스팅 상태 메타
 * ================================================================ */

const HOSTING_STATUS_META = {
  'OPEN': { label: '신청가능', className: 'badge-open' },
  'FULL': { label: '모집완료', className: 'badge-full' },
  'FIXED': { label: '확정', className: 'badge-full' },
  'FAILED': { label: '취소됨', className: 'badge-failed' },
  'IN_PROGRESS': { label: '진행중', className: 'badge-progress' },
  'CLOSED': { label: '완료', className: 'badge-closed' },
};

export function getStatusMeta(status) {
  return HOSTING_STATUS_META[status] ?? { label: status ?? '-', className: 'badge-closed' };
}

/* ================================================================
 * 5. 날짜·시간 포맷
 * ================================================================ */

function formatTime(date) {
  return new Intl.DateTimeFormat('ko-KR', {
    timeZone: KST_TIME_ZONE,
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date);
}

function formatDate(date) {
  return new Intl.DateTimeFormat('ko-KR', {
    timeZone: KST_TIME_ZONE,
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  }).format(date);
}

export function formatHostingDate(hostingAt) {
  const startDate = parseApiDateTime(hostingAt);
  if (!startDate || Number.isNaN(startDate.getTime())) {
    return '-';
  }
  return formatDate(startDate);
}

export function formatHostingTimeRange(hostingAt, hostingEnd) {
  const startDate = parseApiDateTime(hostingAt);
  const endDate = parseApiDateTime(hostingEnd);

  if (!startDate || Number.isNaN(startDate.getTime())
    || !endDate || Number.isNaN(endDate.getTime())) {
    return '-';
  }

  return `${formatTime(startDate)} ~ ${formatTime(endDate)}`;
}

export function formatDateTimeRange(hostingAt, hostingEnd) {
  const startDate = parseApiDateTime(hostingAt);
  const endDate = parseApiDateTime(hostingEnd);

  if (!startDate || Number.isNaN(startDate.getTime())
    || !endDate || Number.isNaN(endDate.getTime())) {
    return '-';
  }

  return `${formatDate(startDate)} · ${formatTime(startDate)} ~ ${formatTime(endDate)}`;
}

export function getHostingDurationHours(hostingAt, hostingEnd) {
  const startDate = parseApiDateTime(hostingAt);
  const endDate = parseApiDateTime(hostingEnd);

  if (!startDate || Number.isNaN(startDate.getTime())
    || !endDate || Number.isNaN(endDate.getTime())) {
    return null;
  }

  const durationMs = endDate.getTime() - startDate.getTime();
  const durationHours = durationMs / (60 * 60 * 1000);

  if (!Number.isFinite(durationHours) || durationHours <= 0) {
    return null;
  }

  return Number.isInteger(durationHours)
    ? String(durationHours)
    : durationHours.toFixed(1);
}

export function formatHostingTimeRangeWithDuration(hostingAt, hostingEnd) {
  const timeRangeText = formatHostingTimeRange(hostingAt, hostingEnd);
  const durationHours = getHostingDurationHours(hostingAt, hostingEnd);

  if (timeRangeText === '-' || !durationHours) {
    return timeRangeText;
  }

  return `${timeRangeText} (${durationHours}시간 진행)`;
}

export function formatDateTimeRangeWithDuration(hostingAt, hostingEnd) {
  const dateTimeRangeText = formatDateTimeRange(hostingAt, hostingEnd);
  const durationHours = getHostingDurationHours(hostingAt, hostingEnd);

  if (dateTimeRangeText === '-' || !durationHours) {
    return dateTimeRangeText;
  }

  return `${dateTimeRangeText} (${durationHours}시간 진행)`;
}

/* ================================================================
 * 6. 호스팅 데이터 헬퍼
 * ================================================================ */

export function buildHostingAddressText(hosting) {
  const baseAddress = [hosting?.address?.road_address, hosting?.address?.detail_address]
    .filter(Boolean)
    .join(' ')
    .trim();

  if (!baseAddress) {
    return hosting?.address?.building_name ?? '';
  }

  if (!hosting?.address?.building_name) {
    return baseAddress;
  }

  return `${baseAddress} (${hosting.address.building_name})`;
}

export function getCurrentPeopleCount(hosting) {
  return Number(hosting?.current_people ?? 0);
}

export function formatHostingPeopleText(hosting) {
  const currentPeople = getCurrentPeopleCount(hosting);
  const maxPeople = Number(hosting?.max_people ?? 0);
  return `${currentPeople}/${maxPeople}명`;
}

/**
 * 호스팅의 검색 키워드 타깃 문자열 생성
 * @param {object} hosting
 * @param {string[]} extraTokens 페이지별 추가 키워드 (예: 어르신 이름)
 */
export function buildHostingKeywordTarget(hosting, extraTokens = []) {
  return [
    hosting.menu,
    hosting.address?.sigungu,
    hosting.address?.bname,
    hosting.address?.road_address,
    hosting.address?.detail_address,
    hosting.address?.building_name,
    ...extraTokens,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
}

/* ================================================================
 * 7. 호스팅 카드 빌더
 *    페이지별 차이점은 옵션으로 주입
 * ================================================================ */

/**
 * 호스팅 카드 DOM 생성
 *
 * @param {object} hosting 호스팅 데이터
 * @param {object} options
 * @param {string} options.title       카드 상단 큰 타이틀 (예: "강남구 · 역삼동 호스팅" / "홍길동 어르신")
 * @param {string} options.avatarText  아바타에 표시할 한 글자
 * @param {string} options.ariaLabel   접근성 라벨
 * @param {string[]} [options.extraKeywordTokens] 검색 키워드에 추가할 값
 * @param {object} [options.dataset]   data-* 속성으로 추가할 키-값
 * @param {string} options.helperText  하단 헬퍼 텍스트 (예: "모집 인원 1/4명")
 * @param {string} options.actionsHtml 카드 액션 영역 HTML
 * @param {string} [options.extraBadgesHtml] 상태 뱃지 옆에 추가할 보조 뱃지 HTML
 * @param {Function} options.onActivate (hosting) => void  카드 클릭/Enter 처리
 * @returns {HTMLElement}
 */
export function buildHostingCard(hosting, options) {
  const {
    title,
    avatarText,
    ariaLabel,
    extraKeywordTokens = [],
    dataset = {},
    helperText,
    actionsHtml,
    extraBadgesHtml = '',
    onActivate,
  } = options;

  const statusMeta = getStatusMeta(hosting.hosting_status);
  const addressText = buildHostingAddressText(hosting);

  const cardElement = document.createElement('article');
  cardElement.className = 'card hosting-card slide-up';
  cardElement.dataset.sigungu = hosting.address?.sigungu ?? '';
  cardElement.dataset.status = hosting.hosting_status ?? '';
  cardElement.dataset.keyword = buildHostingKeywordTarget(hosting, extraKeywordTokens);

  Object.entries(dataset).forEach(([key, value]) => {
    cardElement.dataset[key] = value;
  });

  cardElement.tabIndex = 0;
  cardElement.setAttribute('role', 'link');
  cardElement.setAttribute('aria-label', ariaLabel);

  const handleActivate = (event) => {
    if (event?.target?.closest?.('.hosting-card-actions a, .hosting-card-actions button')) {
      return;
    }
    onActivate?.(hosting);
  };

  cardElement.addEventListener('click', handleActivate);
  cardElement.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onActivate?.(hosting);
    }
  });

  cardElement.innerHTML = `
    <div class="card-body">
      <div class="hosting-header">
        <div class="hosting-avatar">${escapeHtml(avatarText)}</div>
        <div class="hosting-header-text">
          <div class="hosting-name" title="${escapeHtml(title)}">${escapeHtml(title)}</div>
          <div class="hosting-address" title="${escapeHtml(addressText || '-')}">${escapeHtml(addressText || '-')}</div>
        </div>
      </div>

      <div class="hosting-menu" title="${escapeHtml(hosting.menu || '-')}">${escapeHtml(hosting.menu || '-')}</div>

      <div class="hosting-status-row hosting-status-row-after-menu">
        <span class="badge hosting-status-badge ${statusMeta.className}">
          ${escapeHtml(statusMeta.label)}
        </span>
        ${extraBadgesHtml}
      </div>

      <div class="hosting-meta">
        <div class="hosting-meta-row">
          <span class="hosting-meta-label">날짜</span>
          <span class="hosting-meta-value">${escapeHtml(formatHostingDate(hosting.hosting_at))}</span>
        </div>
        <div class="hosting-meta-row">
          <span class="hosting-meta-label">시간</span>
          <span class="hosting-meta-value">${escapeHtml(formatHostingTimeRangeWithDuration(hosting.hosting_at, hosting.hosting_end))}</span>
        </div>
      </div>

      <div class="hosting-helper">${escapeHtml(helperText)}</div>

      <div class="hosting-card-actions">
        ${actionsHtml}
      </div>
    </div>
  `;

  return cardElement;
}

/* ================================================================
 * 8. 시군구 셀렉트 옵션 렌더
 * ================================================================ */

export function renderSigunguOptions(selectElement, hostingItems) {
  if (!selectElement) {
    return;
  }
  const previousValue = selectElement.value;

  const sigunguSet = new Set(
    hostingItems
      .map((hosting) => hosting.address?.sigungu ?? '')
      .filter(Boolean)
  );

  selectElement.innerHTML = '<option value="">전체 시군구</option>';

  [...sigunguSet]
    .sort((left, right) => left.localeCompare(right, 'ko'))
    .forEach((sigungu) => {
      selectElement.appendChild(new Option(sigungu, sigungu));
    });

  selectElement.value = [...sigunguSet].includes(previousValue) ? previousValue : '';
}

/* ================================================================
 * 9. 알림 모달 (info / success / error)
 *    공통 마크업: <div class="alert-modal-overlay" id="alert-modal"> ... </div>
 *    필요 ID: alert-modal, alert-modal-panel, alert-modal-title,
 *             alert-modal-message, alert-modal-confirm
 * ================================================================ */

let alertModalResolver = null;

function getAlertModalTitle(type) {
  if (type === 'success') return '완료';
  if (type === 'error') return '오류';
  return '안내';
}

export function showAlertModal(message, type = 'info') {
  return new Promise((resolve) => {
    const overlay = document.querySelector('#alert-modal');
    const panel = document.querySelector('#alert-modal-panel');
    const titleElement = document.querySelector('#alert-modal-title');
    const messageElement = document.querySelector('#alert-modal-message');

    if (!overlay || !panel || !titleElement || !messageElement) {
      console.warn('alert-modal 마크업이 없어 모달을 표시할 수 없어요.');
      resolve();
      return;
    }

    panel.className = `alert-modal ${type}`;
    titleElement.textContent = getAlertModalTitle(type);
    messageElement.textContent = message;
    overlay.classList.add('open');
    document.body.classList.add('modal-open');
    alertModalResolver = resolve;
  });
}

export function closeAlertModal() {
  const overlay = document.querySelector('#alert-modal');
  if (!overlay) {
    return;
  }
  overlay.classList.remove('open');
  document.body.classList.remove('modal-open');

  if (alertModalResolver) {
    const resolve = alertModalResolver;
    alertModalResolver = null;
    resolve();
  }
}

export function isAlertModalOpen() {
  return document.querySelector('#alert-modal')?.classList.contains('open') ?? false;
}

/**
 * 알림 모달의 기본 이벤트 (확인 버튼, 바깥 클릭, ESC) 바인딩
 * @param {object} [options]
 * @param {boolean} [options.closeOnBackdrop=true] 바깥 클릭 시 닫기
 * @param {boolean} [options.closeOnEscape=true]   ESC 시 닫기
 */
export function bindAlertModalEvents(options = {}) {
  const { closeOnBackdrop = true, closeOnEscape = true } = options;

  document.querySelector('#alert-modal-confirm')?.addEventListener('click', closeAlertModal);

  if (closeOnBackdrop) {
    document.querySelector('#alert-modal')?.addEventListener('click', (event) => {
      if (event.target === event.currentTarget) {
        closeAlertModal();
      }
    });
  }

  if (closeOnEscape) {
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && isAlertModalOpen()) {
        closeAlertModal();
      }
    });
  }
}
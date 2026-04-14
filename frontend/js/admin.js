/**
 * 관리자 페이지 공통 유틸
 * 관리자 전용 페이지에서 공통으로 사용하기위해 생성
 */

// ── 인증 / 권한 확인 ─────────────────────────────────────
function denyAccess() {
  document.getElementById('accessDenied').classList.add('show');
  setTimeout(() => window.location.replace('/pages/login.html'), 2500);
}

async function checkAdmin() {
  if (!isLoggedIn()) { denyAccess(); return false; }
  try {
    const me = await api('/users/me');
    if (me.user_role !== 'admin') { denyAccess(); return false; }
  } catch {
    denyAccess(); return false;
  }
  return true;
}

// ── 토스트 ───────────────────────────────────────────────
function showToast(msg, type = '') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show ' + type;
  setTimeout(() => { el.className = 'toast'; }, 2500);
}

// ── 유틸 ────────────────────────────────────────────────
function formatDate(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleDateString('ko-KR', { month: 'long', day: 'numeric' });
}

function formatDatetime(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}


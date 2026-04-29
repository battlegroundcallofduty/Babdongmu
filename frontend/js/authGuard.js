const STORAGE_KEY = 'currentUser';
const ACCESS_TOKEN_KEY = 'access_token';
const SESSION_KEY = 'cachedUser';
const SESSION_TTL = 5 * 60 * 1000;

function removeCachedUser() {
  window.localStorage.removeItem(STORAGE_KEY);
}

function removeAccessToken() {
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export function getCachedCurrentUser() {
  const raw = window.localStorage.getItem(STORAGE_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    removeCachedUser();
    return null;
  }
}

export function setCurrentUser(user) {
  if (!user) {
    removeCachedUser();
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
}

export function clearCurrentUser() {
  removeCachedUser();
}

export function clearAuth() {
  removeCachedUser();
  removeAccessToken();
  sessionStorage.removeItem(SESSION_KEY);
}

export function isLoggedIn() {
  return Boolean(window.localStorage.getItem(ACCESS_TOKEN_KEY));
}

export function redirectToLogin() {
  clearAuth();
  window.location.replace('/pages/login.html');
}

export async function fetchCurrentUser() {
  if (!isLoggedIn()) {
    return null;
  }

  const cached = sessionStorage.getItem(SESSION_KEY);
  if (cached) {
    try {
      const { user, at } = JSON.parse(cached);
      if (Date.now() - at < SESSION_TTL) {
        return user;
      }
    } catch {
      sessionStorage.removeItem(SESSION_KEY);
    }
  }

  try {
    const me = await api('/users/me');
    setCurrentUser(me);
    sessionStorage.setItem(SESSION_KEY, JSON.stringify({ user: me, at: Date.now() }));
    return me;
  } catch (error) {
    clearAuth();
    return null;
  }
}

export async function getCurrentUser() {
  return await fetchCurrentUser();
}

export async function requireAuth() {
  const currentUser = await fetchCurrentUser();

  if (!currentUser) {
    redirectToLogin();
    return null;
  }

  if (currentUser.user_role !== 'admin' && currentUser.cert_flag !== 'approved') {
    window.location.replace('/pages/mypage.html');
    return null;
  }

  return currentUser;
}

export function redirectByRole(userRole) {
  if (userRole === 'guardian') {
    window.location.replace('/pages/guardian.html');
    return;
  }

  if (userRole === 'volunteer') {
    window.location.replace('/pages/hosting-match.html');
    return;
  }

  if (userRole === 'admin') {
    window.location.replace('/pages/admin.html');
    return;
  }

  redirectToLogin();
}

export async function requireRoles(allowedRoles = []) {
  const currentUser = await requireAuth();

  if (!currentUser) {
    return null;
  }

  if (!allowedRoles.includes(currentUser.user_role)) {
    redirectByRole(currentUser.user_role);
    return null;
  }
  return currentUser;
}

export async function validateHostingDetailAccess(viewMode) {
  const currentUser = await fetchCurrentUser();

  if (!currentUser) {
    return false;
  }

  if (viewMode === 'guardian') {
    return currentUser.user_role === 'guardian';
  }

  if (viewMode === 'volunteer') {
    return ['volunteer', 'admin'].includes(currentUser.user_role);
  }

  return false;
}

const STORAGE_KEY = 'currentUser';

export function getCurrentUser() {
  const raw = window.localStorage.getItem(STORAGE_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch (error) {
    window.localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function setCurrentUser(user) {
  if (!user) {
    window.localStorage.removeItem(STORAGE_KEY);
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
}

export function clearCurrentUser() {
  window.localStorage.removeItem(STORAGE_KEY);
}

export function requireAuth() {
  const currentUser = getCurrentUser();

  if (!currentUser) {
    window.location.replace('/pages/login.html');
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

  window.location.replace('/pages/login.html');
}

export function requireRoles(allowedRoles = []) {
  const currentUser = requireAuth();

  if (!currentUser) {
    return null;
  }

  if (!allowedRoles.includes(currentUser.user_role)) {
    redirectByRole(currentUser.user_role);
    return null;
  }

  return currentUser;
}

export function validateHostingDetailAccess(viewMode, userRole) {
  if (viewMode === 'guardian') {
    return ['guardian', 'admin'].includes(userRole);
  }

  if (viewMode === 'volunteer') {
    return ['volunteer', 'admin'].includes(userRole);
  }

  return false;
}
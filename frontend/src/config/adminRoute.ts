const rawPrefix = (import.meta.env.VITE_ADMIN_ROUTE_PREFIX || '/admin-console').trim();

function normalizePrefix(prefix: string) {
  const cleaned = prefix.replace(/^\/+|\/+$/g, '');
  return cleaned ? `/${cleaned}` : '/admin-console';
}

export const ADMIN_ROUTE_PREFIX = normalizePrefix(rawPrefix);
export const ADMIN_LOGIN_PATH = `${ADMIN_ROUTE_PREFIX}/login`;
export const ADMIN_REGISTER_PATH = `${ADMIN_ROUTE_PREFIX}/register`;
export const ADMIN_HOME_PATH = `${ADMIN_ROUTE_PREFIX}/dashboard`;
export const ADMIN_SYSTEM_PATH = `${ADMIN_ROUTE_PREFIX}/system`;

export function toAdminPath(path: string) {
  if (!path || path === '/') return ADMIN_HOME_PATH;
  if (path === ADMIN_ROUTE_PREFIX || path.startsWith(`${ADMIN_ROUTE_PREFIX}/`)) return path;
  return `${ADMIN_ROUTE_PREFIX}${path.startsWith('/') ? path : `/${path}`}`;
}


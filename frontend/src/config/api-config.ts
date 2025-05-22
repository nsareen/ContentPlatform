/**
 * Centralized API configuration
 * This file contains all API-related configuration to avoid hardcoding values across multiple files
 */

// Detect environment
export const isDevelopment = process.env.NODE_ENV !== 'production';

// Detect if we're running in the browser preview proxy
export const isProxyEnvironment = typeof window !== 'undefined' && 
  window.location.hostname.includes('127.0.0.1') && 
  !['3000', '3001', '3002', '3003', '3004', '3005'].includes(window.location.port);

// Backend port - centralized to avoid inconsistencies
export const BACKEND_PORT = 8000;

// API base URL with proper formatting
export const API_BASE_URL = isProxyEnvironment 
  ? '' 
  : `http://localhost:${BACKEND_PORT}`;

// Direct backend URL for use in browser preview
export const DIRECT_BACKEND_URL = `http://localhost:${BACKEND_PORT}`;

// API prefix used by the backend
export const API_PREFIX = '/api';

// Debug the actual API URL construction
if (isDevelopment) {
  console.log(`[API Config] Base URL: ${API_BASE_URL}`);
  console.log(`[API Config] API Prefix: ${API_PREFIX}`);
  console.log(`[API Config] Sample endpoint: ${API_BASE_URL}${API_PREFIX}/voices`);
}

// Auth endpoints
export const AUTH_ENDPOINTS = {
  TOKEN: `${API_BASE_URL}${API_PREFIX}/token`,
  DEV_TOKEN: `${API_BASE_URL}${API_PREFIX}/dev-token`,
  REFRESH: `${API_BASE_URL}${API_PREFIX}/refresh`,
};

// Brand voice endpoints
export const BRAND_VOICE_ENDPOINTS = {
  LIST: `${API_BASE_URL}${API_PREFIX}/voices/`,
  DETAIL: (id: string) => `${API_BASE_URL}${API_PREFIX}/voices/${id}/`,
  ANALYZE: (id: string) => `${API_BASE_URL}${API_PREFIX}/voices/${id}/analyze/`,
  VERSIONS: (id: string) => `${API_BASE_URL}${API_PREFIX}/voices/${id}/versions/`,
  RESTORE_VERSION: (voiceId: string, versionId: string) => 
    `${API_BASE_URL}${API_PREFIX}/voices/${voiceId}/versions/${versionId}/restore/`,
};

// Rich content endpoints
export const RICH_CONTENT_ENDPOINTS = {
  GENERATE: `${API_BASE_URL}${API_PREFIX}/rich-content/generate/`,
  TEMPLATES: `${API_BASE_URL}${API_PREFIX}/rich-content/templates/`,
};

// Request timeout in milliseconds
export const REQUEST_TIMEOUT = 30000; // 30 seconds

// Helper function to ensure URLs are properly formatted for FastAPI endpoints
export const ensureTrailingSlash = (url: string): string => {
  // Don't modify protocol slashes
  if (url.endsWith('://')) {
    return url;
  }
  
  // For URLs with query parameters
  if (url.includes('?')) {
    const [path, query] = url.split('?');
    return path.endsWith('/') ? `${path}?${query}` : `${path}/?${query}`;
  }
  
  // For all other URLs, add trailing slash if not present (FastAPI routes expect trailing slashes)
  return url.endsWith('/') || url.endsWith('://') ? url : `${url}/`;
};

// Log configuration in development
if (isDevelopment) {
  console.log('[API Config] Environment:', isDevelopment ? 'Development' : 'Production');
  console.log('[API Config] Proxy environment:', isProxyEnvironment);
  console.log('[API Config] API base URL:', API_BASE_URL);
}

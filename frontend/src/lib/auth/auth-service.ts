/**
 * Centralized authentication service for managing auth tokens
 * This provides a consistent way to handle authentication across the application
 */

// Import centralized API configuration
import { 
  API_BASE_URL, 
  AUTH_ENDPOINTS, 
  isProxyEnvironment, 
  REQUEST_TIMEOUT 
} from '../../config/api-config';

// Token endpoints from centralized config
const TOKEN_URL = AUTH_ENDPOINTS.TOKEN;
const DEV_TOKEN_URL = AUTH_ENDPOINTS.DEV_TOKEN;

// Development mode detection
const isDevelopment = process.env.NODE_ENV !== 'production';
const isClient = typeof window !== 'undefined';
const hostname = isClient ? window.location.hostname : '';
const isLocalhost = isClient && (hostname === 'localhost' || hostname === '127.0.0.1');

// Log configuration in development mode
if (isDevelopment) {
  console.log(`[Auth Service] API base URL: ${API_BASE_URL}`);
  console.log(`[Auth Service] Token URL: ${TOKEN_URL}`);
  console.log(`[Auth Service] Dev token URL: ${DEV_TOKEN_URL}`);
  console.log(`[Auth Service] Environment: ${isDevelopment ? 'Development' : 'Production'}`);
  console.log(`[Auth Service] Client: ${isClient}, Hostname: ${hostname}, Localhost: ${isLocalhost}`);
}

// Token refresh settings
const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes
const TOKEN_STORAGE_KEY = 'auth_token';

/**
 * Decode a JWT token to get its payload
 */
const decodeToken = (token: string): any => {
  try {
    // Split the token into parts
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }
    
    // Decode the payload (middle part)
    const payload = parts[1];
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join('')
    );
    
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('[Auth Service] Error decoding token:', error);
    return null;
  }
};

/**
 * Check if a token is expired or about to expire
 */
const isTokenExpired = (token: string): boolean => {
  const payload = decodeToken(token);
  if (!payload || !payload.exp) {
    return true; // If we can't decode the token or it has no expiration, consider it expired
  }
  
  const expirationTime = payload.exp * 1000; // Convert from seconds to milliseconds
  return Date.now() >= expirationTime - TOKEN_REFRESH_THRESHOLD;
};

/**
 * Create a development token for testing
 */
const createDevelopmentToken = (): string => {
  if (isDevelopment) {
    console.log('[Auth Service] Creating development token');
    
    // Create a simple header with algorithm and token type
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    
    // Create a payload with common JWT claims
    const now = Math.floor(Date.now() / 1000);
    const payload = btoa(JSON.stringify({
      sub: 'user-123',
      name: 'Development User',
      tenant_id: 'tenant-123',
      role: 'admin',
      iat: now,
      exp: now + 3600 // Expires in 1 hour
    }));
    
    // Create a simple signature (not secure, but fine for development)
    const signature = 'development-signature-not-for-production-use';
    
    // Combine all parts to form a JWT token
    return `${header}.${payload}.${signature}`;
  }
  
  throw new Error('Development token should only be created in development mode');
};

/**
 * Get a development token from the server
 */
const getDevelopmentToken = async (): Promise<string> => {
  if (isDevelopment) {
    console.log('[Auth Service] Attempting to get development token from:', DEV_TOKEN_URL);
  }
  
  try {
    // First try with POST method and JSON body (which is what the FastAPI endpoint expects)
    try {
      const response = await fetch(DEV_TOKEN_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ username: 'admin@example.com' }),
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (isDevelopment) {
          console.log('[Auth Service] Got development token from server using POST');
        }
        return data.access_token;
      }
      
      if (isDevelopment) {
        console.log(`[Auth Service] POST request failed with status: ${response.status}`);
      }
    } catch (postError) {
      console.error('[Auth Service] Error getting development token with POST:', postError);
    }
    
    // Fallback to GET method if POST fails
    const response = await fetch(DEV_TOKEN_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      credentials: 'include'
    });
    
    if (response.ok) {
      const data = await response.json();
      if (isDevelopment) {
        console.log('[Auth Service] Got development token from server using GET');
      }
      return data.access_token;
    }
    
    throw new Error(`Failed to get development token: ${response.status}`);
  } catch (error) {
    console.error('[Auth Service] All attempts to get development token failed:', error);
    
    // As a fallback, create a local development token
    if (isDevelopment) {
      console.log('[Auth Service] Falling back to local development token');
      return createDevelopmentToken();
    }
    
    throw error;
  }
};

/**
 * Get a token using credentials
 */
const getTokenWithCredentials = async (): Promise<string> => {
  try {
    if (isDevelopment) {
      console.log('[Auth Service] Attempting to get token with credentials from:', TOKEN_URL);
    }
    
    const formData = new URLSearchParams();
    formData.append('username', 'admin@example.com');
    formData.append('password', 'password123');
    
    // Try using XMLHttpRequest for better control over the request
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      xhr.open('POST', TOKEN_URL, true);
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.setRequestHeader('Accept', 'application/json');
      xhr.withCredentials = true;
      xhr.timeout = REQUEST_TIMEOUT;
      
      xhr.onload = function() {
        if (isDevelopment) {
          console.log(`[Auth Service] Token request completed with status: ${xhr.status}`);
          console.log(`[Auth Service] Response headers: ${xhr.getAllResponseHeaders()}`);
        }
        
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            if (data && data.access_token) {
              if (isDevelopment) {
                console.log('[Auth Service] Successfully obtained token with credentials');
              }
              resolve(data.access_token);
            } else {
              reject(new Error('Token response did not contain access_token'));
            }
          } catch (error) {
            const parseError = error as Error;
            reject(new Error(`Failed to parse token response: ${parseError.message}`));
          }
        } else {
          reject(new Error(`Failed to get token with credentials: ${xhr.status}`));
        }
      };
      
      xhr.onerror = function() {
        console.error('[Auth Service] Network error during token request');
        reject(new Error('Network error during token request'));
      };
      
      xhr.ontimeout = function() {
        console.error('[Auth Service] Token request timed out');
        reject(new Error('Token request timed out'));
      };
      
      xhr.send(formData.toString());
    });
  } catch (error) {
    console.error('[Auth Service] Error getting token with credentials:', error);
    
    // Fallback to fetch API if XMLHttpRequest fails
    try {
      console.log('[Auth Service] Falling back to fetch API for token request');
      
      const formData = new URLSearchParams();
      formData.append('username', 'admin@example.com');
      formData.append('password', 'password123');
      
      const response = await fetch(TOKEN_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        },
        body: formData.toString(),
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (isDevelopment) {
          console.log('[Auth Service] Got token with credentials using fetch fallback');
        }
        return data.access_token;
      }
      
      throw new Error(`Fetch fallback failed with status: ${response.status}`);
    } catch (fetchError) {
      console.error('[Auth Service] Fetch fallback also failed:', fetchError);
      throw error; // Throw the original error
    }
  }
};

/**
 * Get token from localStorage
 */
const getStoredToken = (): string | null => {
  if (isClient) {
    return localStorage.getItem(TOKEN_STORAGE_KEY);
  }
  return null;
};

/**
 * Clear the authentication token from localStorage
 */
const clearAuthToken = (): void => {
  if (isClient) {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    if (isDevelopment) {
      console.log('[Auth Service] Cleared token from localStorage');
    }
  }
};

/**
 * Get the authentication token, refreshing if necessary
 */
const getAuthToken = async (): Promise<string> => {
  if (isDevelopment) {
    console.log('[Auth Service] getAuthToken called');
  }
  
  // Check if we have a token in localStorage
  const storedToken = getStoredToken();
  
  // If we have a token and it's not expired, return it
  if (storedToken && !isTokenExpired(storedToken)) {
    if (isDevelopment) {
      console.log('[Auth Service] Using existing token from localStorage');
    }
    return storedToken;
  }
  
  if (isDevelopment) {
    console.log('[Auth Service] Token not found or expired, attempting to get a new one');
  }
  
  try {
    // Try to get a development token first if in development mode
    if (isDevelopment) {
      try {
        console.log('[Auth Service] Trying to get development token');
        const devToken = await getDevelopmentToken();
        setAuthToken(devToken);
        console.log('[Auth Service] Successfully obtained and saved development token');
        return devToken;
      } catch (devError) {
        console.error('[Auth Service] Failed to get development token:', devError);
      }
    }
    
    // Try to get a token with credentials
    console.log('[Auth Service] Trying to get token with credentials');
    const token = await getTokenWithCredentials();
    setAuthToken(token);
    console.log('[Auth Service] Successfully obtained and saved token with credentials');
    return token;
  } catch (error) {
    console.error('[Auth Service] All standard token retrieval methods failed:', error);
    
    // Last resort: try XMLHttpRequest directly to the token endpoint
    try {
      console.log('[Auth Service] Attempting direct XMLHttpRequest to token endpoint');
      
      const token = await new Promise<string>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', TOKEN_URL, true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.withCredentials = true;
        
        xhr.onload = function() {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const data = JSON.parse(xhr.responseText);
              if (data && data.access_token) {
                resolve(data.access_token);
              } else {
                reject(new Error('Token response did not contain access_token'));
              }
            } catch (error) {
              reject(new Error(`Failed to parse token response: ${(error as Error).message}`));
            }
          } else {
            reject(new Error(`Token request failed with status: ${xhr.status}`));
          }
        };
        
        xhr.onerror = function() {
          reject(new Error('Network error during token request'));
        };
        
        const formData = new URLSearchParams();
        formData.append('username', 'admin@example.com');
        formData.append('password', 'password123');
        xhr.send(formData.toString());
      });
      
      setAuthToken(token);
      console.log('[Auth Service] Successfully obtained token via direct XMLHttpRequest');
      return token;
    } catch (xhrError) {
      console.error('[Auth Service] Direct XMLHttpRequest also failed:', xhrError);
    }
    
    // If we're in development mode, create a local token as absolute last resort
    if (isDevelopment) {
      console.log('[Auth Service] Creating local development token as last resort');
      const localToken = createDevelopmentToken();
      setAuthToken(localToken);
      return localToken;
    }
    
    throw new Error('Failed to get authentication token after trying all methods');
  }
};

/**
 * Check if the user is authenticated
 */
const isAuthenticated = (): boolean => {
  const token = getStoredToken();
  return !!token && !isTokenExpired(token);
};

/**
 * Set the authentication token in localStorage
 */
const setAuthToken = (token: string): void => {
  if (isClient) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
    if (isDevelopment) {
      console.log('[Auth Service] Saved token to localStorage');
    }
  }
};

/**
 * Create headers for API requests with authentication
 */
const createAuthHeaders = async (): Promise<HeadersInit> => {
  try {
    const token = await getAuthToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  } catch (error) {
    // If we can't get a token, return headers without authorization
    console.error('[Auth Service] Failed to create auth headers:', error);
    return {
      'Content-Type': 'application/json'
    };
  }
};

/**
 * Make an authenticated API request with retry logic and improved error handling
 * Using XMLHttpRequest for maximum compatibility
 */
const makeAuthenticatedRequest = async <T>(
  url: string, 
  method: string = 'GET', 
  body?: any,
  signal?: AbortSignal,
  retryCount: number = 0
): Promise<T> => {
  try {
    // Maximum number of retries
    const maxRetries = 3;
    
    // Backoff factor for exponential backoff
    const backoffFactor = 2;
    
    // Get auth token
    let token = '';
    try {
      token = await getAuthToken();
    } catch (tokenError) {
      console.error('[Auth Service] Failed to get auth token:', tokenError);
      
      // In development mode, try to proceed without a token
      if (isDevelopment) {
        console.warn('[Auth Service] Proceeding without authentication token in development mode');
      } else {
        throw new Error('Authentication failed: No valid token available');
      }
    }
    
    // Ensure URL is absolute
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url.startsWith('/') ? '' : '/'}${url}`;
    
    // Log the full request details for debugging
    console.log(`[Auth Service] Request: ${method} ${fullUrl}`, {
      hasToken: !!token,
      tokenLength: token ? token.length : 0,
      hasBody: !!body,
      retryCount,
      isLocalhost,
      isDevelopment
    });
    
    return new Promise<T>((resolve, reject) => {
      // Track if the request was aborted
      let aborted = false;
      
      // Setup abort handling
      if (signal) {
        if (signal.aborted) {
          aborted = true;
          reject(new Error('Request aborted'));
          return;
        }
        
        signal.addEventListener('abort', () => {
          aborted = true;
          xhr.abort();
          reject(new Error('Request aborted'));
        });
      }
      
      // Create XMLHttpRequest
      const xhr = new XMLHttpRequest();
      
      // Set timeout
      xhr.timeout = 30000; // 30 seconds
      
      // Setup handlers
      xhr.onload = function() {
        if (aborted) return;
        
        // Log response headers for debugging
        console.log(`[Auth Service] Response status: ${xhr.status}`);
        console.log(`[Auth Service] Response headers:`, xhr.getAllResponseHeaders());
        
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            // Handle empty response
            if (!xhr.responseText.trim()) {
              resolve({} as T);
              return;
            }
            
            // Parse JSON response
            const response = JSON.parse(xhr.responseText);
            resolve(response as T);
          } catch (e: any) {
            console.error('[Auth Service] Error parsing response:', e);
            reject(new Error(`Failed to parse response: ${e.message || 'Unknown error'}`));
          }
        } else if (xhr.status === 401 || xhr.status === 403) {
          console.error(`[Auth Service] Authentication failed: ${xhr.status}`);
          console.error(`[Auth Service] Response: ${xhr.responseText}`);
          
          // Clear invalid token
          clearAuthToken();
          
          // Retry with a new token if we haven't exceeded max retries
          if (retryCount < maxRetries) {
            const delay = Math.pow(backoffFactor, retryCount) * 1000; // Exponential backoff
            console.log(`[Auth Service] Authentication failed, retrying (${retryCount + 1}/${maxRetries}) after ${delay}ms...`);
            setTimeout(() => {
              makeAuthenticatedRequest<T>(url, method, body, signal, retryCount + 1)
                .then((result: T) => resolve(result))
                .catch((err: any) => reject(err));
            }, delay);
            return;
          }
          
          // Parse error response
          let errorText;
          try {
            errorText = xhr.responseText || `Status ${xhr.status}`;
          } catch (e) {
            errorText = `Status ${xhr.status}`;
          }
          
          reject(new Error(`Authentication error: ${xhr.status} - ${xhr.statusText} - ${errorText}`));
        } else {
          // Handle other error status codes
          console.error(`[Auth Service] API error: ${xhr.status}`);
          console.error(`[Auth Service] Response: ${xhr.responseText}`);
          
          // Retry server errors (5xx) if we haven't exceeded max retries
          if (xhr.status >= 500 && retryCount < maxRetries) {
            const delay = Math.pow(backoffFactor, retryCount) * 1000;
            console.log(`[Auth Service] Server error, retrying (${retryCount + 1}/${maxRetries}) after ${delay}ms...`);
            
            setTimeout(() => {
              makeAuthenticatedRequest<T>(url, method, body, signal, retryCount + 1)
                .then((result: T) => resolve(result))
                .catch((err: any) => reject(err));
            }, delay);
            return;
          }
          
          // Parse error response
          let errorText;
          try {
            errorText = xhr.responseText || `Status ${xhr.status}`;
          } catch (e) {
            errorText = `Status ${xhr.status}`;
          }
          
          reject(new Error(`API error: ${xhr.status} - ${xhr.statusText} - ${errorText}`));
        }
      };
      
      xhr.onerror = function() {
        if (aborted) return;
        
        console.error('[Auth Service] Network error occurred');
        
        // Retry network errors with exponential backoff
        if (retryCount < maxRetries) {
          const delay = Math.pow(backoffFactor, retryCount) * 1000;
          console.log(`[Auth Service] Network error, retrying (${retryCount + 1}/${maxRetries}) after ${delay}ms...`);
          
          setTimeout(() => {
            makeAuthenticatedRequest<T>(url, method, body, signal, retryCount + 1)
              .then((result: T) => resolve(result))
              .catch((err: any) => reject(err));
          }, delay);
          return;
        }
        
        reject(new Error('Network error: Failed to connect to the server. Please check your connection.'));
      };
      
      xhr.ontimeout = function() {
        if (aborted) return;
        
        console.error('[Auth Service] Request timed out');
        
        // Retry timeouts with exponential backoff
        if (retryCount < maxRetries) {
          const delay = Math.pow(backoffFactor, retryCount) * 1000;
          console.log(`[Auth Service] Request timed out, retrying (${retryCount + 1}/${maxRetries}) after ${delay}ms...`);
          
          setTimeout(() => {
            makeAuthenticatedRequest<T>(url, method, body, signal, retryCount + 1)
              .then((result: T) => resolve(result))
              .catch((err: any) => reject(err));
          }, delay);
          return;
        }
        
        reject(new Error('Request timed out. The server is taking too long to respond.'));
      };
      
      // Open and send request
      xhr.open(method, fullUrl, true);
      
      // Set headers
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader('Accept', 'application/json');
      
      // Add authorization header if token exists
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      
      // Enable credentials for CORS
      xhr.withCredentials = true;
      
      // Send with or without body
      if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        xhr.send(JSON.stringify(body));
      } else {
        xhr.send();
      }
    });
  } catch (error: any) {
    // Log detailed error information
    console.error('[Auth Service] Request failed:', error);
    console.error('[Auth Service] Error message:', error.message || 'Unknown error');
    console.error('[Auth Service] Error stack:', error.stack || 'No stack trace');
    
    // Rethrow the error to be handled by the caller
    throw error;
  }
};

export default {
  getAuthToken,
  isAuthenticated,
  setAuthToken,
  clearAuthToken,
  createAuthHeaders,
  makeAuthenticatedRequest
};

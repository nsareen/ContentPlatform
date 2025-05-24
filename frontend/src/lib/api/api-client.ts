/**
 * API Client for making requests to the backend
 * 
 * This client handles all API requests to the backend, including:
 * - Authentication
 * - Error handling
 * - Request/response logging
 * - URL normalization
 */
import { API_BASE_URL, API_PREFIX, isDevelopment, isProxyEnvironment } from '../../config/api-config';

// Log configuration in development
if (isDevelopment) {
  console.log('[API Client] Environment:', isDevelopment ? 'Development' : 'Production');
  console.log('[API Client] Proxy environment:', isProxyEnvironment);
  console.log('[API Client] API base URL:', API_BASE_URL);
  console.log('[API Client] API prefix:', API_PREFIX);
}

interface ApiClientOptions {
  baseUrl?: string;
  headers?: Record<string, string>;
}

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  credentials?: RequestCredentials;
}

class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl || API_BASE_URL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers,
    };
    
    if (isDevelopment) {
      console.log('[API Client] Initialized with base URL:', this.baseUrl);
    }
  }

  // Set the authorization token for authenticated requests
  setAuthToken(token: string) {
    if (token) {
      if (isDevelopment) {
        console.log('[API Client] Setting auth token');
      }
      this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  // Clear the authorization token
  clearAuthToken() {
    if (isDevelopment) {
      console.log('[API Client] Clearing auth token');
    }
    delete this.defaultHeaders['Authorization'];
  }

  /**
   * Normalize an endpoint URL to ensure it works with the backend
   * 
   * Our FastAPI backend has different URL format requirements for different endpoints:
   * - Auth endpoints: no trailing slashes
   * - Brand voice endpoints: trailing slashes required
   * - Rich content endpoints: trailing slashes required
   * 
   * This method ensures all URLs are properly formatted based on the endpoint type.
   */
  private normalizeUrl(endpoint: string): string {
    // If it's already a full URL, just ensure proper formatting
    if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
      // For full URLs, we still need to check endpoint type and format accordingly
      const isAuthEndpoint = endpoint.includes('/token') || endpoint.includes('/refresh');
      const isBrandVoiceEndpoint = endpoint.includes('/voices');
      const isRichContentEndpoint = endpoint.includes('/rich-content');
      
      if (isAuthEndpoint) {
        // Auth endpoints should NOT have trailing slashes
        return endpoint.endsWith('/') ? endpoint.slice(0, -1) : endpoint;
      } else if (isBrandVoiceEndpoint || isRichContentEndpoint) {
        // Brand voice and rich content endpoints MUST have trailing slashes
        return endpoint.endsWith('/') ? endpoint : `${endpoint}/`;
      }
      return endpoint;
    }
    
    // Handle relative endpoints
    // First, ensure consistent formatting with the base URL
    let url = endpoint.startsWith('/') ? `${this.baseUrl}${endpoint}` : `${this.baseUrl}/${endpoint}`;
    
    // Detect endpoint type
    const isAuthEndpoint = url.includes('/token') || url.includes('/refresh');
    const isBrandVoiceEndpoint = url.includes('/voices');
    const isRichContentEndpoint = url.includes('/rich-content');
    
    if (isDevelopment) {
      console.log(`[API Client] Normalizing URL: ${endpoint}`);
      console.log(`[API Client] Base URL: ${this.baseUrl}`);
      console.log(`[API Client] Initial URL: ${url}`);
      console.log(`[API Client] Is auth endpoint: ${isAuthEndpoint}`);
      console.log(`[API Client] Is brand voice endpoint: ${isBrandVoiceEndpoint}`);
      console.log(`[API Client] Is rich content endpoint: ${isRichContentEndpoint}`);
    }
    
    // Apply endpoint-specific formatting
    if (isAuthEndpoint) {
      // Auth endpoints should NOT have trailing slashes
      if (url.endsWith('/') && !url.endsWith('://')) {
        url = url.slice(0, -1);
      }
    } else if (isBrandVoiceEndpoint || isRichContentEndpoint) {
      // Brand voice and rich content endpoints MUST have trailing slashes
      if (!url.endsWith('/')) {
        url = `${url}/`;
      }
    }
    
    if (isDevelopment) {
      console.log(`[API Client] Normalized URL: ${endpoint} → ${url}`);
    }
    
    return url;
  }

  /**
   * Make a request to the API
   */
  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const url = this.normalizeUrl(endpoint);
    const { method = 'GET', headers = {}, body, credentials = 'include' } = options;
    
    // Get auth token from localStorage
    const token = localStorage.getItem('auth_token');
    
    // Prepare headers
    const requestHeaders: Record<string, string> = {
      ...this.defaultHeaders,
      ...headers,
    };
    
    // Add auth token if available
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    // Prepare request options
    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      credentials,
    };
    
    // Add body for non-GET requests
    if (body && method !== 'GET') {
      if (requestHeaders['Content-Type'] === 'application/x-www-form-urlencoded') {
        requestOptions.body = body;
      } else {
        requestOptions.body = JSON.stringify(body);
      }
    }
    
    // Log request in development
    if (isDevelopment) {
      console.log(`[API Client] ${method} ${url}`);
      console.log('[API Client] Headers:', requestHeaders);
      if (body) {
        console.log('[API Client] Body:', body);
      }
    }
    
    try {
      // Make the request
      const response = await fetch(url, requestOptions);
      
      // Log response in development
      if (isDevelopment) {
        console.log(`[API Client] Response status: ${response.status}`);
        console.log('[API Client] Response headers:', Object.fromEntries([...response.headers.entries()]));
      }
      
      // Handle no content responses
      if (response.status === 204) {
        return {} as T;
      }
      
      // Parse response based on content type
      let data: any;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }
      
      // Log response data in development
      if (isDevelopment) {
        if (typeof data === 'string') {
          console.log(`[API Client] Response text: ${data.substring(0, 200)}${data.length > 200 ? '...' : ''}`);
        } else {
          console.log('[API Client] Response data:', data);
        }
      }
      
      // Handle error responses
      if (!response.ok) {
        const errorMessage = typeof data === 'object' && data.detail
          ? data.detail
          : `Request failed with status ${response.status}`;
        
        throw new Error(errorMessage);
      }
      
      return data as T;
    } catch (error) {
      // Log and rethrow errors
      console.error(`[API Client] Request failed: ${error instanceof Error ? error.message : String(error)}`);
      throw error;
    }
  }

  // Helper methods for common HTTP methods
  async get<T>(endpoint: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', headers });
  }

  async post<T>(endpoint: string, body?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body, headers });
  }

  async put<T>(endpoint: string, body?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body, headers });
  }

  async delete<T>(endpoint: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE', headers });
  }
}

// Create and export a singleton instance
export const apiClient = new ApiClient();

export default apiClient;

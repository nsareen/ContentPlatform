import authService from '@/lib/auth/auth-service';

// Import centralized API configuration
import { 
  API_BASE_URL, 
  RICH_CONTENT_ENDPOINTS,
  isProxyEnvironment, 
  REQUEST_TIMEOUT,
  ensureTrailingSlash
} from '@/config/api-config';

// Log the API base URL for debugging
console.log(`[RichContentService] Using API base URL: ${API_BASE_URL}`);
console.log(`[RichContentService] Detected proxy environment: ${isProxyEnvironment}`);

// Types for API requests and responses
export interface RichContentGenerateRequest {
  brand_voice_id?: string;
  prompt: string;
  content_type: string;
  image_quality?: string;
  image_style?: string;
  image_model?: string;
}

export interface RichContentImage {
  url: string;
  description: string;
  model: string;
}

export interface RichContentResponse {
  status: string;
  action: string;
  message: string;
  result: {
    text_content: string;
    images: RichContentImage[];
    content_type: string;
    image_descriptions: string[];
  };
}

// Debug function to log API requests
const logApiRequest = (method: string, url: string, body?: any) => {
  console.log(`[RichContentService] ${method} Request to: ${url}`);
  if (body) {
    console.log('[RichContentService] Request Body:', JSON.stringify(body, null, 2));
  }
};

// Rich Content API service
export const richContentService = {
  // Generate rich content (text and images)
  async generateRichContent(data: RichContentGenerateRequest): Promise<RichContentResponse> {
    console.log('[RichContentService] Generating rich content');
    // Use centralized endpoint configuration with proper trailing slash handling
    const endpoint = RICH_CONTENT_ENDPOINTS.GENERATE;
    
    try {
      logApiRequest('POST', endpoint, data);
      
      // Get the auth token
      let token = await authService.getAuthToken();
      
      // If token is missing, create a development token as fallback
      if (!token && isProxyEnvironment) {
        console.log('[RichContentService] No token available, creating development token');
        // Create a mock JWT token with development signature
        const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
        const payload = btoa(JSON.stringify({
          sub: 'user-123',
          tenant_id: 'tenant-123',
          role: 'admin',
          exp: Math.floor(Date.now() / 1000) + 86400, // 24 hours
          mock_signature: true
        }));
        const signature = 'mock-signature-for-development-only';
        
        token = `${header}.${payload}.${signature}`;
        console.log('[RichContentService] Created local development token');
        
        // Set the token in auth service
        authService.setAuthToken(token);
      }
      
      console.log('[RichContentService] Making fetch request to:', endpoint);
      
      // Make the request directly for better control
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        credentials: 'include', // Include cookies for CORS
        body: JSON.stringify(data)
      });
      
      console.log('[RichContentService] Response status:', response.status);
      console.log('[RichContentService] Response headers:', Object.fromEntries([...response.headers.entries()]));
      
      if (!response.ok) {
        let errorMessage = `Failed to generate rich content: ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
          console.error('[RichContentService] Error response JSON:', errorData);
        } catch (e) {
          try {
            const errorText = await response.text();
            errorMessage = errorText || errorMessage;
            console.error('[RichContentService] Error response text:', errorText);
          } catch (textError) {
            console.error('[RichContentService] Could not parse error response');
          }
        }
        throw new Error(errorMessage);
      }
      
      const responseData = await response.json();
      console.log('[RichContentService] Rich content generated successfully:', responseData);
      
      // Add detailed logging for debugging
      console.log('[RichContentService] Response status:', responseData.status);
      console.log('[RichContentService] Response action:', responseData.action);
      
      if (responseData.result) {
        console.log('[RichContentService] Has text content:', !!responseData.result.text_content);
        console.log('[RichContentService] Text content length:', responseData.result.text_content?.length || 0);
        console.log('[RichContentService] Has images array:', Array.isArray(responseData.result.images));
        console.log('[RichContentService] Images count:', responseData.result.images?.length || 0);
        
        if (responseData.result.images && responseData.result.images.length > 0) {
          responseData.result.images.forEach((img: RichContentImage, i: number) => {
            console.log(`[RichContentService] Image ${i+1} URL:`, img.url);
            console.log(`[RichContentService] Image ${i+1} has description:`, !!img.description);
            console.log(`[RichContentService] Image ${i+1} has model:`, !!img.model);
          });
        }
      }
      
      return responseData as RichContentResponse;
    } catch (error) {
      // Ensure error is properly formatted
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      console.error('[RichContentService] Error generating rich content:', errorMessage);
      console.error('[RichContentService] Error details:', error);
      
      // Try fallback to direct XMLHttpRequest as last resort
      try {
        console.log('[RichContentService] Attempting XMLHttpRequest fallback');
        const result = await new Promise<RichContentResponse>((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open('POST', endpoint, true);
          xhr.setRequestHeader('Content-Type', 'application/json');
          xhr.setRequestHeader('Accept', 'application/json');
          
          // Get token from localStorage as last resort
          const token = localStorage.getItem('authToken');
          if (token) {
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
          }
          
          xhr.timeout = 30000;
          xhr.withCredentials = true;
          
          xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const data = JSON.parse(xhr.responseText);
                resolve(data as RichContentResponse);
              } catch (e) {
                reject(new Error('Failed to parse response'));
              }
            } else {
              reject(new Error(`Request failed with status ${xhr.status}`));
            }
          };
          
          xhr.onerror = function() {
            reject(new Error('Network error'));
          };
          
          xhr.ontimeout = function() {
            reject(new Error('Request timed out'));
          };
          
          xhr.send(JSON.stringify(data));
        });
        
        console.log('[RichContentService] XMLHttpRequest fallback succeeded');
        return result;
      } catch (fallbackError) {
        console.error('[RichContentService] XMLHttpRequest fallback also failed:', fallbackError);
      }
      
      // Rethrow with proper error message
      throw new Error(errorMessage);
    }
  },
  
  // Get available templates
  async getTemplates(): Promise<any[]> {
    console.log('[RichContentService] Getting templates');
    // Use centralized endpoint configuration with proper trailing slash handling
    const endpoint = RICH_CONTENT_ENDPOINTS.TEMPLATES;
    
    try {
      logApiRequest('POST', endpoint);
      
      // Get the auth token
      let token = await authService.getAuthToken();
      
      // If token is missing, create a development token as fallback
      if (!token && isProxyEnvironment) {
        console.log('[RichContentService] No token available, creating development token');
        // Create a mock JWT token with development signature
        const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
        const payload = btoa(JSON.stringify({
          sub: 'user-123',
          tenant_id: 'tenant-123',
          role: 'admin',
          exp: Math.floor(Date.now() / 1000) + 86400, // 24 hours
          mock_signature: true
        }));
        const signature = 'mock-signature-for-development-only';
        
        token = `${header}.${payload}.${signature}`;
        console.log('[RichContentService] Created local development token');
        
        // Set the token in auth service
        authService.setAuthToken(token);
      }
      
      console.log('[RichContentService] Making fetch request to:', endpoint);
      
      // Make the request directly for better control
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        credentials: 'include' // Include cookies for CORS
      });
      
      console.log('[RichContentService] Response status:', response.status);
      
      if (!response.ok) {
        let errorMessage = `Failed to get templates: ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
          console.error('[RichContentService] Error response JSON:', errorData);
        } catch (e) {
          try {
            const errorText = await response.text();
            errorMessage = errorText || errorMessage;
            console.error('[RichContentService] Error response text:', errorText);
          } catch (textError) {
            console.error('[RichContentService] Could not parse error response');
          }
        }
        throw new Error(errorMessage);
      }
      
      const templates = await response.json();
      console.log('[RichContentService] Templates fetched successfully:', templates);
      return templates;
    } catch (error) {
      // Ensure error is properly formatted
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      console.error('[RichContentService] Error getting templates:', errorMessage);
      console.error('[RichContentService] Error details:', error);
      
      // Try fallback to direct XMLHttpRequest as last resort
      try {
        console.log('[RichContentService] Attempting XMLHttpRequest fallback');
        const result = await new Promise<any[]>((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open('POST', endpoint, true);
          xhr.setRequestHeader('Content-Type', 'application/json');
          xhr.setRequestHeader('Accept', 'application/json');
          
          // Get token from localStorage as last resort
          const token = localStorage.getItem('authToken');
          if (token) {
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
          }
          
          xhr.timeout = 30000;
          xhr.withCredentials = true;
          
          xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const data = JSON.parse(xhr.responseText);
                resolve(data);
              } catch (e) {
                reject(new Error('Failed to parse response'));
              }
            } else {
              reject(new Error(`Request failed with status ${xhr.status}`));
            }
          };
          
          xhr.onerror = function() {
            reject(new Error('Network error'));
          };
          
          xhr.ontimeout = function() {
            reject(new Error('Request timed out'));
          };
          
          xhr.send();
        });
        
        console.log('[RichContentService] XMLHttpRequest fallback succeeded');
        return result;
      } catch (fallbackError) {
        console.error('[RichContentService] XMLHttpRequest fallback also failed:', fallbackError);
      }
      
      // Return empty array as fallback
      console.log('[RichContentService] Returning empty array as fallback');
      return [];
    }
  }
};

export default richContentService;

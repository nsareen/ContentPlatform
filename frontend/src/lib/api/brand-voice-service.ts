/**
 * Brand Voice Service
 * 
 * This service handles all API requests related to brand voices, including:
 * - Creating, updating, and deleting brand voices
 * - Fetching brand voice details and versions
 * - Analyzing content against brand voice guidelines
 */
import { DIRECT_BACKEND_URL, API_BASE_URL, API_PREFIX } from '@/config/api-config';
import { isDevelopment } from '@/config/api-config';
import type { BrandVoice, BrandVoiceUpdateRequest, BrandVoiceVersion } from '@/types/brand-voice';

// Types for API requests and responses
export interface BrandVoiceCreateRequest {
  tenant_id: string;
  name: string;
  description: string;
  voice_metadata?: {
    personality?: string;
    tonality?: string;
  };
  personality?: string;
  tonality?: string;
  dos?: string;
  donts?: string;
}

// Use the centralized API base URL
const BACKEND_URL = API_BASE_URL;

// Hardcoded token for development - updated with a fresh token from the dev-token endpoint
const DEV_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDc5NzcxNzV9.iRGPvHgK3GaH3ZDwgbfpZBgOhCCYe7pLRl3c1YROj6c';

/**
 * Fetch function that uses the Next.js API proxy configured in next.config.ts
 * This approach leverages the existing rewrites configuration
 */
async function apiFetch<T>(endpoint: string, method: string = 'GET', body?: any): Promise<T> {
  // Construct the URL using the API_BASE_URL from config
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Log detailed information about the request
  console.log(`[BrandVoiceService] Making ${method} request to URL: ${url}`);
  if (body) {
    console.log(`[BrandVoiceService] Request body: ${JSON.stringify(body).substring(0, 100)}...`);
  }
  
  try {
    // Make the request
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEV_TOKEN}`
      },
      body: body ? JSON.stringify(body) : undefined
    });
    
    // Log response information
    console.log(`[BrandVoiceService] Response received from: ${url}`);
    console.log(`[BrandVoiceService] Response status: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      console.error(`[BrandVoiceService] Request failed with status ${response.status} for URL: ${url}`);
      throw new Error(`Request failed with status ${response.status}`);
    }
    
    // Parse the response
    const data = await response.json();
    return data as T;
  } catch (error) {
    console.error(`[BrandVoiceService] Request failed for URL ${url}:`, error);
    throw error;
  }
}

/**
 * Brand Voice API Service
 */
export interface BrandVoiceGenerateRequest {
  content: string;
  brand_name?: string;
  industry?: string;
  target_audience?: string;
  options?: {
    generation_depth?: string;
    include_sample_content?: boolean;
  };
}

export interface BrandVoiceComponents {
  personality_traits: string[];
  tonality: string;
  identity: string;
  dos: string[];
  donts: string[];
  sample_content: string;
}

export interface BrandVoiceSaveRequest {
  brand_voice_components: BrandVoiceComponents;
  generation_metadata: any;
  source_content: string;
  name: string;
  description?: string;
  tenant_id?: string;
}

export const brandVoiceService = {
  /**
   * Get all brand voices
   */
  async getAllBrandVoices(tenantId?: string): Promise<BrandVoice[]> {
    try {
      // Use direct backend URL to bypass Next.js proxy issues
      // The backend endpoint is defined WITH a trailing slash
      const directUrl = `${DIRECT_BACKEND_URL}/api/voices/all/`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Fetching all brand voices with direct URL: ${directUrl}`);
      }
      
      // Make the request directly to the backend
      const response = await fetch(directUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${DEV_TOKEN}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      
      const voices = await response.json() as BrandVoice[];
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Retrieved ${voices.length} brand voices`);
      }
      
      return voices;
    } catch (error) {
      console.error('[BrandVoiceService] Failed to get brand voices:', error);
      throw error;
    }
  },

  /**
   * Create a new brand voice
   */
  async createBrandVoice(data: BrandVoiceCreateRequest): Promise<BrandVoice> {
    try {
      const endpoint = '/api/voices';
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Creating brand voice: ${endpoint}`);
        console.log(`[BrandVoiceService] Create data:`, data);
      }
      
      const createdVoice = await apiFetch<BrandVoice>(endpoint, 'POST', data);
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Created brand voice: ${createdVoice.name}`);
      }
      
      return createdVoice;
    } catch (error) {
      console.error('[BrandVoiceService] Failed to create brand voice:', error);
      throw error;
    }
  },

  /**
   * Update an existing brand voice
   */
  async updateBrandVoice(id: string, data: BrandVoiceUpdateRequest): Promise<BrandVoice> {
    try {
      // Use direct backend URL to bypass Next.js proxy issues
      const directUrl = `${DIRECT_BACKEND_URL}/api/voices/${id}`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Updating brand voice with direct URL: ${directUrl}`);
        console.log(`[BrandVoiceService] Update data:`, data);
      }
      
      // Make the request directly to the backend
      const response = await fetch(directUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${DEV_TOKEN}`
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[BrandVoiceService] Server error response:`, errorText);
        throw new Error(`Request failed with status ${response.status}`);
      }
      
      const updatedVoice = await response.json() as BrandVoice;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Updated brand voice: ${updatedVoice.name}`);
      }
      
      return updatedVoice;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to update brand voice with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get a specific brand voice by ID
   */
  async getBrandVoice(id: string): Promise<BrandVoice> {
    try {
      const endpoint = `/api/voices/${id}`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Fetching brand voice: ${endpoint}`);
      }
      
      const voice = await apiFetch<BrandVoice>(endpoint, 'GET');
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Retrieved brand voice: ${voice.name}`);
      }
      
      return voice;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to get brand voice with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a brand voice
   */
  async deleteBrandVoice(id: string): Promise<void> {
    try {
      const endpoint = `/api/voices/${id}`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Deleting brand voice: ${endpoint}`);
      }
      
      await apiFetch<void>(endpoint, 'DELETE');
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Deleted brand voice with ID ${id}`);
      }
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to delete brand voice with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Publish a brand voice (changes status to published)
   */
  async publishBrandVoice(id: string): Promise<BrandVoice> {
    try {
      const endpoint = `/api/voices/${id}`;
      const updateData = { status: 'published' };
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Publishing brand voice: ${endpoint}`);
      }
      
      const publishedVoice = await apiFetch<BrandVoice>(endpoint, 'PUT', updateData);
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Published brand voice with ID ${id}`);
      }
      
      return publishedVoice;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to publish brand voice with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Analyze text to generate brand voice suggestions
   */
  async analyzeBrandVoice(id: string, corpus: string): Promise<any> {
    try {
      const endpoint = `/api/voices/${id}/analyze`;
      const requestData = { corpus };
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Analyzing brand voice: ${endpoint}`);
      }
      
      const analysisResult = await apiFetch<any>(endpoint, 'POST', requestData);
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Analyzed brand voice with ID ${id}`);
      }
      
      return analysisResult;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to analyze brand voice with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get all versions of a brand voice
   */
  async getBrandVoiceVersions(voiceId: string): Promise<BrandVoiceVersion[]> {
    try {
      const endpoint = `/api/voices/${voiceId}/versions`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Fetching versions: ${endpoint}`);
      }
      
      const versions = await apiFetch<BrandVoiceVersion[]>(endpoint, 'GET');
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Retrieved ${versions.length} versions for brand voice ${voiceId}`);
      }
      
      return versions;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to get versions for brand voice with ID ${voiceId}:`, error);
      throw error;
    }
  },

  /**
   * Restore a previous version of a brand voice
   */
  async restoreBrandVoiceVersion(voiceId: string, versionNumber: number): Promise<BrandVoice> {
    try {
      const endpoint = `/api/voices/${voiceId}/versions/${versionNumber}/restore`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Restoring version: ${endpoint}`);
      }
      
      const restoredVoice = await apiFetch<BrandVoice>(endpoint, 'POST');
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Restored version ${versionNumber} for brand voice ${voiceId}`);
      }
      
      return restoredVoice;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to restore version ${versionNumber} for brand voice ${voiceId}:`, error);
      throw error;
    }
  },
  
  /**
   * Analyze content against a brand voice (legacy method)
   */
  async analyzeBrandVoiceContent(voiceId: string, content: string): Promise<any> {
    try {
      const endpoint = `/api/voices/${voiceId}/analyze`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Analyzing content: ${endpoint}`);
      }
      
      const analysis = await apiFetch<any>(endpoint, 'POST', { content });
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Analyzed content against brand voice ${voiceId}`);
      }
      
      return analysis;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to analyze content against brand voice ${voiceId}:`, error);
      throw error;
    }
  },
  
  /**
   * Analyze content using the new brand voice analyzer
   * This uses the LangGraph-based analyzer for more detailed analysis
   */
  async analyzeBrandVoiceWithLangGraph(voiceId: string, content: string, options?: any): Promise<any> {
    try {
      // Use DIRECT_BACKEND_URL for consistent behavior with other endpoints
      // Note the trailing slash which is required by FastAPI
      const endpoint = `${DIRECT_BACKEND_URL}/api/brand-voice-analyzer/analyze/`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Analyzing content with LangGraph analyzer: ${endpoint}`);
      }
      
      // Default options for analysis
      const defaultOptions = {
        analysis_depth: "detailed",
        include_suggestions: true,
        highlight_issues: true,
        max_suggestions: 5,
        generate_report: true
      };
      
      const analysisOptions = options ? { ...defaultOptions, ...options } : defaultOptions;
      
      const analysis = await apiFetch<any>(endpoint, 'POST', { 
        content,
        brand_voice_id: voiceId,
        options: analysisOptions
      });
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Analyzed content with LangGraph analyzer for brand voice ${voiceId}`);
      }
      
      return analysis;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to analyze content with LangGraph analyzer for brand voice ${voiceId}:`, error);
      throw error;
    }
  },

  /**
   * Generate a brand voice profile from sample content
   */
  async generateBrandVoice(data: BrandVoiceGenerateRequest): Promise<any> {
    try {
      // Use DIRECT_BACKEND_URL for consistent behavior with other endpoints
      // Note the trailing slash which is required by FastAPI
      const endpoint = `${DIRECT_BACKEND_URL}/api/brand-voice-generator/generate/`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Generating brand voice: ${endpoint}`);
      }
      
      const result = await apiFetch<any>(endpoint, 'POST', data);
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Brand voice generated successfully`);
      }
      
      return result;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to generate brand voice:`, error);
      throw error;
    }
  },

  /**
   * Save a generated brand voice profile
   */
  async saveBrandVoice(data: BrandVoiceSaveRequest): Promise<any> {
    try {
      // Use DIRECT_BACKEND_URL for consistent behavior with other endpoints
      const endpoint = `${DIRECT_BACKEND_URL}/api/brand-voice-generator/save/`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Saving generated brand voice: ${endpoint}`);
      }
      
      const result = await apiFetch<any>(endpoint, 'POST', data);
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Generated brand voice saved successfully`);
      }
      
      return result;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to save generated brand voice:`, error);
      throw error;
    }
  },

  /**
   * Refine a generated brand voice based on feedback
   */
  async refineBrandVoice(data: any): Promise<any> {
    try {
      // Use DIRECT_BACKEND_URL for consistent behavior with other endpoints
      const endpoint = `${DIRECT_BACKEND_URL}/api/brand-voice-generator/refine/`;
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Refining brand voice: ${endpoint}`);
      }
      
      const result = await apiFetch<any>(endpoint, 'POST', data);
      
      if (isDevelopment) {
        console.log(`[BrandVoiceService] Brand voice refined successfully`);
      }
      
      return result;
    } catch (error) {
      console.error(`[BrandVoiceService] Failed to refine brand voice:`, error);
      throw error;
    }
  }
};

export default brandVoiceService;

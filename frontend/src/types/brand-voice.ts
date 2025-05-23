/**
 * Brand Voice Types
 * 
 * This file contains TypeScript interfaces for brand voice data structures
 */

export interface BrandVoice {
  id: string;
  name: string;
  description: string;
  voice_metadata: {
    personality: string;
    tonality: string;
    [key: string]: any;
  };
  dos: string;
  donts: string;
  tenant_id: string;
  version: number;
  status: 'draft' | 'published' | 'archived';
  created_by_id: string;
  created_at: string;
  updated_at: string | null;
  published_at: string | null;
}

export interface BrandVoiceUpdateRequest {
  name?: string;
  description?: string;
  voice_metadata?: {
    personality?: string;
    tonality?: string;
    [key: string]: any;
  };
  dos?: string;
  donts?: string;
  status?: 'draft' | 'published' | 'archived';
}

export interface BrandVoiceVersion {
  id: string;
  brand_voice_id: string;
  version_number: number;
  name: string;
  description: string;
  voice_metadata: {
    personality: string;
    tonality: string;
    [key: string]: any;
  };
  dos: string;
  donts: string;
  status: 'draft' | 'published' | 'archived';
  created_by_id: string;
  created_at: string;
  published_at: string | null;
}

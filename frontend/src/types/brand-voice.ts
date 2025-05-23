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
  status: 'draft' | 'published' | 'under_review' | 'inactive';
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
  status?: 'draft' | 'published' | 'under_review' | 'inactive';
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
  status: 'draft' | 'published' | 'under_review' | 'inactive';
  created_by: string;
  created_by_id?: string;
  created_at: string;
  updated_at?: string | null;
  published_at: string | null;
}

/**
 * Version Comparison Types
 */

// Type for representing a change in a field between versions
export type ChangeType = 'added' | 'removed' | 'modified' | 'unchanged';

// Represents a difference in a specific field between versions
export interface VersionDiff {
  field: string;          // The field that changed (can be a nested path like 'voice_metadata.personality')
  oldValue: any;          // The value in the base version
  newValue: any;          // The value in the compared version
  changeType: ChangeType; // The type of change
  displayName: string;    // User-friendly name for the field
}

// Represents a complete comparison between two versions
export interface VersionComparison {
  baseVersion: BrandVoiceVersion;     // The base version for comparison
  comparedVersion: BrandVoiceVersion; // The version being compared against the base
  differences: VersionDiff[];         // List of differences between versions
}

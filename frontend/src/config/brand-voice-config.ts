/**
 * Brand Voice Configuration
 * 
 * This file contains centralized configuration for brand voice functionality
 */

export const BRAND_VOICE_CONFIG = {
  // Status options for brand voices
  STATUS: {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    ARCHIVED: 'archived'
  },
  
  // Configuration for version comparison
  VERSION_COMPARISON: {
    HIGHLIGHT_CHANGES: true,
    MAX_VERSIONS_TO_COMPARE: 2,
    DIFF_COLORS: {
      ADDED: '#e6ffed',
      REMOVED: '#ffeef0',
      MODIFIED: '#f8f0fd',
      UNCHANGED: '#ffffff'
    }
  },
  
  // Fields to display in the comparison view
  COMPARABLE_FIELDS: [
    { key: 'name', label: 'Name' },
    { key: 'description', label: 'Description' },
    { key: 'voice_metadata.personality', label: 'Personality' },
    { key: 'voice_metadata.tonality', label: 'Tonality' },
    { key: 'dos', label: 'Dos' },
    { key: 'donts', label: "Don'ts" },
    { key: 'status', label: 'Status' }
  ]
};

export default BRAND_VOICE_CONFIG;

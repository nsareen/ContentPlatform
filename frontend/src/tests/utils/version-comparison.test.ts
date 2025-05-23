import { 
  compareVersions,
  formatValueForDisplay,
  getChangeColor,
  areVersionsDifferent,
  getVersionChangeSummary
} from '@/utils/version-comparison';
import { BrandVoiceVersion, ChangeType } from '@/types/brand-voice';
import { BRAND_VOICE_CONFIG } from '@/config/brand-voice-config';

// Mock the brand voice config
jest.mock('@/config/brand-voice-config', () => ({
  BRAND_VOICE_CONFIG: {
    COMPARABLE_FIELDS: [
      { key: 'name', label: 'Name' },
      { key: 'description', label: 'Description' },
      { key: 'voice_metadata.personality', label: 'Personality' },
      { key: 'voice_metadata.tonality', label: 'Tonality' },
      { key: 'dos', label: 'Do\'s' },
      { key: 'donts', label: 'Don\'ts' },
      { key: 'status', label: 'Status' }
    ],
    VERSION_COMPARISON: {
      MAX_VERSIONS_TO_COMPARE: 2,
      DIFF_COLORS: {
        ADDED: 'green-50',
        REMOVED: 'red-50',
        MODIFIED: 'amber-50',
        UNCHANGED: 'white'
      }
    }
  }
}));

describe('Version Comparison Utilities', () => {
  // Sample brand voice versions for testing
  const baseVersion: BrandVoiceVersion = {
    id: '1',
    brand_voice_id: 'bv-1',
    version_number: 1,
    name: 'Original Voice',
    description: 'Initial version',
    voice_metadata: {
      personality: 'Professional',
      tonality: 'Formal'
    },
    dos: 'Be concise',
    donts: 'Avoid jargon',
    status: 'published',
    created_at: '2025-05-20T10:00:00Z',
    updated_at: '2025-05-20T10:00:00Z',
    created_by: 'user-1'
  };
  
  const modifiedVersion: BrandVoiceVersion = {
    id: '2',
    brand_voice_id: 'bv-1',
    version_number: 2,
    name: 'Updated Voice',
    description: 'Initial version',
    voice_metadata: {
      personality: 'Friendly',
      tonality: 'Casual'
    },
    dos: 'Be concise\nUse simple language',
    donts: 'Avoid jargon',
    status: 'draft',
    created_at: '2025-05-21T10:00:00Z',
    updated_at: '2025-05-21T10:00:00Z',
    created_by: 'user-1'
  };

  describe('compareVersions', () => {
    it('should identify differences between versions', () => {
      const comparison = compareVersions(baseVersion, modifiedVersion);
      
      expect(comparison.differences).toHaveLength(4); // name, personality, tonality, status, dos changed
      
      // Check that specific fields are identified as changed
      const changedFields = comparison.differences.map(diff => diff.field);
      expect(changedFields).toContain('name');
      expect(changedFields).toContain('voice_metadata.personality');
      expect(changedFields).toContain('voice_metadata.tonality');
      expect(changedFields).toContain('status');
      expect(changedFields).toContain('dos');
      
      // Verify unchanged fields aren't included
      expect(changedFields).not.toContain('description');
      expect(changedFields).not.toContain('donts');
    });
    
    it('should correctly identify the type of change', () => {
      const comparison = compareVersions(baseVersion, modifiedVersion);
      
      // Find the name change and check its properties
      const nameChange = comparison.differences.find(diff => diff.field === 'name');
      expect(nameChange).toBeDefined();
      expect(nameChange?.oldValue).toBe('Original Voice');
      expect(nameChange?.newValue).toBe('Updated Voice');
      expect(nameChange?.changeType).toBe('modified');
      expect(nameChange?.displayName).toBe('Name');
    });
  });
  
  describe('formatValueForDisplay', () => {
    it('should format values appropriately for display', () => {
      // Test null/undefined handling
      expect(formatValueForDisplay(null, 'name')).toBe('—');
      expect(formatValueForDisplay(undefined, 'description')).toBe('—');
      
      // Test status formatting
      expect(formatValueForDisplay('draft', 'status')).toBe('Draft');
      expect(formatValueForDisplay('published', 'status')).toBe('Published');
      
      // Test object formatting
      const obj = { key: 'value' };
      expect(formatValueForDisplay(obj, 'metadata')).toContain('key');
      expect(formatValueForDisplay(obj, 'metadata')).toContain('value');
      
      // Test string formatting
      expect(formatValueForDisplay('test', 'name')).toBe('test');
    });
  });
  
  describe('getChangeColor', () => {
    it('should return the correct color for each change type', () => {
      expect(getChangeColor('added')).toBe('green-50');
      expect(getChangeColor('removed')).toBe('red-50');
      expect(getChangeColor('modified')).toBe('amber-50');
      expect(getChangeColor('unchanged')).toBe('white');
    });
  });
  
  describe('areVersionsDifferent', () => {
    it('should return true when versions have differences', () => {
      expect(areVersionsDifferent(baseVersion, modifiedVersion)).toBe(true);
    });
    
    it('should return false when versions are identical', () => {
      expect(areVersionsDifferent(baseVersion, baseVersion)).toBe(false);
    });
  });
  
  describe('getVersionChangeSummary', () => {
    it('should generate a concise summary of changes', () => {
      const summary = getVersionChangeSummary(baseVersion, modifiedVersion);
      expect(summary).toContain('Changed');
    });
    
    it('should return "No changes" for identical versions', () => {
      const summary = getVersionChangeSummary(baseVersion, baseVersion);
      expect(summary).toBe('No changes');
    });
  });
});

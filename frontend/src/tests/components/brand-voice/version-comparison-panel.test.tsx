import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { VersionComparisonPanel } from '@/components/brand-voice/version-comparison-panel';
import { BrandVoiceVersion } from '@/types/brand-voice';
import * as versionComparisonUtils from '@/utils/version-comparison';

// Mock the version comparison utilities
jest.mock('@/utils/version-comparison', () => ({
  compareVersions: jest.fn(),
  formatValueForDisplay: jest.fn((value) => value ? String(value) : '—'),
  getChangeColor: jest.fn(() => 'test-color'),
}));

// Mock the brand voice config
jest.mock('@/config/brand-voice-config', () => ({
  BRAND_VOICE_CONFIG: {
    COMPARABLE_FIELDS: [
      { key: 'name', label: 'Name' },
      { key: 'description', label: 'Description' }
    ],
    VERSION_COMPARISON: {
      DIFF_COLORS: {
        ADDED: 'green-50',
        REMOVED: 'red-50',
        MODIFIED: 'amber-50',
        UNCHANGED: 'white'
      }
    }
  }
}));

describe('VersionComparisonPanel', () => {
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
  
  const comparedVersion: BrandVoiceVersion = {
    id: '2',
    brand_voice_id: 'bv-1',
    version_number: 2,
    name: 'Updated Voice',
    description: 'Updated description',
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

  // Mock functions
  const onClose = jest.fn();
  const onRestore = jest.fn();
  const onSwapVersions = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup mock comparison result
    (versionComparisonUtils.compareVersions as jest.Mock).mockReturnValue({
      baseVersion,
      comparedVersion,
      differences: [
        {
          field: 'name',
          oldValue: 'Original Voice',
          newValue: 'Updated Voice',
          changeType: 'modified',
          displayName: 'Name'
        },
        {
          field: 'description',
          oldValue: 'Initial version',
          newValue: 'Updated description',
          changeType: 'modified',
          displayName: 'Description'
        }
      ]
    });
  });

  it('renders the comparison panel with version information', () => {
    render(
      <VersionComparisonPanel
        baseVersion={baseVersion}
        comparedVersion={comparedVersion}
        onClose={onClose}
        onRestore={onRestore}
        onSwapVersions={onSwapVersions}
      />
    );
    
    // Check that version numbers are displayed
    expect(screen.getByText(`Version ${baseVersion.version_number}`)).toBeInTheDocument();
    expect(screen.getByText(`Version ${comparedVersion.version_number}`)).toBeInTheDocument();
    
    // Check that field labels are displayed
    expect(screen.getAllByText('Name')).toHaveLength(2);
    expect(screen.getAllByText('Description')).toHaveLength(2);
  });

  it('calls onClose when close button is clicked', () => {
    render(
      <VersionComparisonPanel
        baseVersion={baseVersion}
        comparedVersion={comparedVersion}
        onClose={onClose}
        onRestore={onRestore}
        onSwapVersions={onSwapVersions}
      />
    );
    
    // Find and click the close button
    const closeButton = screen.getByLabelText('Close panel');
    fireEvent.click(closeButton);
    
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onSwapVersions when swap button is clicked', () => {
    render(
      <VersionComparisonPanel
        baseVersion={baseVersion}
        comparedVersion={comparedVersion}
        onClose={onClose}
        onRestore={onRestore}
        onSwapVersions={onSwapVersions}
      />
    );
    
    // Find and click the swap button
    const swapButton = screen.getByLabelText('Swap versions');
    fireEvent.click(swapButton);
    
    expect(onSwapVersions).toHaveBeenCalledTimes(1);
  });

  it('shows restore confirmation dialog when restore is clicked', () => {
    render(
      <VersionComparisonPanel
        baseVersion={baseVersion}
        comparedVersion={comparedVersion}
        onClose={onClose}
        onRestore={onRestore}
        onSwapVersions={onSwapVersions}
      />
    );
    
    // Find and click the first restore button
    const restoreButtons = screen.getAllByText('Restore');
    fireEvent.click(restoreButtons[0]);
    
    // Check that confirmation dialog appears
    expect(screen.getByText(`Restore Version ${baseVersion.version_number}?`)).toBeInTheDocument();
    
    // Confirm restore
    const confirmButton = screen.getByText('Restore Version');
    fireEvent.click(confirmButton);
    
    expect(onRestore).toHaveBeenCalledWith(baseVersion);
  });

  it('cancels restore when cancel button is clicked', () => {
    render(
      <VersionComparisonPanel
        baseVersion={baseVersion}
        comparedVersion={comparedVersion}
        onClose={onClose}
        onRestore={onRestore}
        onSwapVersions={onSwapVersions}
      />
    );
    
    // Find and click the first restore button
    const restoreButtons = screen.getAllByText('Restore');
    fireEvent.click(restoreButtons[0]);
    
    // Find and click the cancel button
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    // Restore should not have been called
    expect(onRestore).not.toHaveBeenCalled();
  });
});

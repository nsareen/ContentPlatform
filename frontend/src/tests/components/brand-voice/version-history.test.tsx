import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { VersionHistory } from '@/components/brand-voice/version-history';
import { brandVoiceService } from '@/lib/api/brand-voice-service';
import { BrandVoiceVersion } from '@/types/brand-voice';

// Mock the brand voice service
jest.mock('@/lib/api/brand-voice-service', () => ({
  brandVoiceService: {
    getBrandVoiceVersions: jest.fn(),
    restoreBrandVoiceVersion: jest.fn(),
  }
}));

// Mock the version comparison panel
jest.mock('@/components/brand-voice/version-comparison-panel', () => ({
  VersionComparisonPanel: jest.fn(({ onClose }) => (
    <div data-testid="mock-comparison-panel">
      <button onClick={onClose}>Close</button>
    </div>
  ))
}));

// Mock the brand voice config
jest.mock('@/config/brand-voice-config', () => ({
  BRAND_VOICE_CONFIG: {
    VERSION_COMPARISON: {
      MAX_VERSIONS_TO_COMPARE: 2,
      DIFF_COLORS: {
        ADDED: 'green-50',
        REMOVED: 'red-50',
        MODIFIED: 'amber-50',
        UNCHANGED: 'white'
      }
    },
    COMPARABLE_FIELDS: [
      { key: 'name', label: 'Name' },
      { key: 'description', label: 'Description' }
    ]
  }
}));

describe('VersionHistory', () => {
  // Sample brand voice versions for testing
  const mockVersions: BrandVoiceVersion[] = [
    {
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
    },
    {
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
    }
  ];

  // Mock functions
  const onVersionRestore = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup mock API responses
    (brandVoiceService.getBrandVoiceVersions as jest.Mock).mockResolvedValue(mockVersions);
    (brandVoiceService.restoreBrandVoiceVersion as jest.Mock).mockResolvedValue({});
    
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
  });

  it('renders version history with loading state and then versions', async () => {
    render(<VersionHistory brandVoiceId="bv-1" onVersionRestore={onVersionRestore} />);
    
    // Should show loading state initially
    expect(screen.getByRole('status')).toBeInTheDocument();
    
    // Wait for versions to load
    await waitFor(() => {
      expect(screen.getByText('Version History')).toBeInTheDocument();
      expect(screen.getByText(`Version ${mockVersions[0].version_number}`)).toBeInTheDocument();
      expect(screen.getByText(`Version ${mockVersions[1].version_number}`)).toBeInTheDocument();
    });
  });

  it('allows selecting versions for comparison', async () => {
    render(<VersionHistory brandVoiceId="bv-1" onVersionRestore={onVersionRestore} />);
    
    // Wait for versions to load
    await waitFor(() => {
      expect(screen.getByText(`Version ${mockVersions[0].version_number}`)).toBeInTheDocument();
    });
    
    // Find and click the checkboxes to select versions
    const versionItems = screen.getAllByRole('checkbox', { hidden: true });
    fireEvent.click(versionItems[0]);
    fireEvent.click(versionItems[1]);
    
    // Should show selection count
    expect(screen.getByText('2 of 2 selected')).toBeInTheDocument();
    
    // Compare button should be enabled
    const compareButton = screen.getByText('Compare');
    expect(compareButton).not.toBeDisabled();
  });

  it('shows comparison panel when compare button is clicked', async () => {
    render(<VersionHistory brandVoiceId="bv-1" onVersionRestore={onVersionRestore} />);
    
    // Wait for versions to load
    await waitFor(() => {
      expect(screen.getByText(`Version ${mockVersions[0].version_number}`)).toBeInTheDocument();
    });
    
    // Select versions
    const versionItems = screen.getAllByRole('checkbox', { hidden: true });
    fireEvent.click(versionItems[0]);
    fireEvent.click(versionItems[1]);
    
    // Click compare button
    const compareButton = screen.getByText('Compare');
    fireEvent.click(compareButton);
    
    // Comparison panel should be shown
    expect(screen.getByTestId('mock-comparison-panel')).toBeInTheDocument();
  });

  it('clears selection when clear button is clicked', async () => {
    render(<VersionHistory brandVoiceId="bv-1" onVersionRestore={onVersionRestore} />);
    
    // Wait for versions to load
    await waitFor(() => {
      expect(screen.getByText(`Version ${mockVersions[0].version_number}`)).toBeInTheDocument();
    });
    
    // Select versions
    const versionItems = screen.getAllByRole('checkbox', { hidden: true });
    fireEvent.click(versionItems[0]);
    
    // Should show selection count
    expect(screen.getByText('1 of 2 selected')).toBeInTheDocument();
    
    // Click clear button
    const clearButton = screen.getByText('Clear');
    fireEvent.click(clearButton);
    
    // Selection count should be gone
    expect(screen.queryByText('1 of 2 selected')).not.toBeInTheDocument();
  });

  it('calls restore API when restore button is clicked', async () => {
    render(<VersionHistory brandVoiceId="bv-1" onVersionRestore={onVersionRestore} />);
    
    // Wait for versions to load
    await waitFor(() => {
      expect(screen.getByText(`Version ${mockVersions[0].version_number}`)).toBeInTheDocument();
    });
    
    // Find and click the restore button
    const restoreButtons = screen.getAllByText('Restore');
    fireEvent.click(restoreButtons[0]);
    
    // Confirm dialog should be shown and accepted (mocked above)
    expect(window.confirm).toHaveBeenCalled();
    
    // API should be called
    expect(brandVoiceService.restoreBrandVoiceVersion).toHaveBeenCalledWith(
      'bv-1', 
      mockVersions[0].version_number
    );
    
    // Callback should be called
    await waitFor(() => {
      expect(onVersionRestore).toHaveBeenCalled();
    });
  });
});

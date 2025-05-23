'use client';

import { useState, useEffect } from 'react';
import { CheckCircle, ArrowLeftRight } from 'lucide-react';
import { BrandVoiceVersion } from '@/types/brand-voice';
import { brandVoiceService } from '@/lib/api/brand-voice-service';
import { VersionComparisonPanel } from './version-comparison-panel';
import { BRAND_VOICE_CONFIG } from '@/config/brand-voice-config';

interface VersionHistoryProps {
  brandVoiceId: string;
  onVersionRestore: () => void;
  currentVersion?: BrandVoiceVersion;
}

export function VersionHistory({ brandVoiceId, onVersionRestore, currentVersion }: VersionHistoryProps) {
  const [versions, setVersions] = useState<BrandVoiceVersion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRestoring, setIsRestoring] = useState(false);
  const [expandedVersionId, setExpandedVersionId] = useState<string | null>(null);
  
  // Version comparison state
  const [selectedVersions, setSelectedVersions] = useState<BrandVoiceVersion[]>([]);
  const [showComparison, setShowComparison] = useState(false);

  useEffect(() => {
    const fetchVersions = async () => {
      try {
        setIsLoading(true);
        const data = await brandVoiceService.getBrandVoiceVersions(brandVoiceId);
        setVersions(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch version history:', err);
        setError('Failed to load version history. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchVersions();
  }, [brandVoiceId]);

  const handleRestore = async (versionNumber: number) => {
    if (window.confirm('Are you sure you want to restore this version? This will create a new version based on the selected one.')) {
      try {
        setIsRestoring(true);
        await brandVoiceService.restoreBrandVoiceVersion(brandVoiceId, versionNumber);
        onVersionRestore();
        setError(null);
      } catch (err) {
        console.error('Failed to restore version:', err);
        setError('Failed to restore version. Please try again.');
      } finally {
        setIsRestoring(false);
      }
    }
  };

  const toggleVersionDetails = (versionId: string) => {
    if (expandedVersionId === versionId) {
      setExpandedVersionId(null);
    } else {
      setExpandedVersionId(versionId);
    }
  };
  
  // Toggle version selection for comparison
  const toggleVersionSelection = (version: BrandVoiceVersion) => {
    if (selectedVersions.some(v => v.id === version.id)) {
      // Deselect if already selected
      setSelectedVersions(selectedVersions.filter(v => v.id !== version.id));
    } else {
      // Select if not at max capacity
      if (selectedVersions.length < BRAND_VOICE_CONFIG.VERSION_COMPARISON.MAX_VERSIONS_TO_COMPARE) {
        setSelectedVersions([...selectedVersions, version]);
      }
    }
  };
  
  // Compare with current version
  const compareWithCurrent = (version: BrandVoiceVersion) => {
    if (currentVersion) {
      setSelectedVersions([currentVersion, version]);
      setShowComparison(true);
    }
  };
  
  // Check if a version is selected
  const isVersionSelected = (versionId: string) => {
    return selectedVersions.some(v => v.id === versionId);
  };
  
  // Swap the order of selected versions
  const swapSelectedVersions = () => {
    if (selectedVersions.length === 2) {
      setSelectedVersions([selectedVersions[1], selectedVersions[0]]);
    }
  };
  
  // Clear all selected versions
  const clearSelectedVersions = () => {
    setSelectedVersions([]);
    setShowComparison(false);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#6D3BEB]"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4">
        {error}
      </div>
    );
  }

  if (versions.length === 0) {
    return (
      <div className="text-center py-8 text-[#475569]">
        No version history available. Changes to this brand voice will be tracked here.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-[#1E2334]">Version History</h3>
        
        {selectedVersions.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-[#475569]">
              {selectedVersions.length} of {BRAND_VOICE_CONFIG.VERSION_COMPARISON.MAX_VERSIONS_TO_COMPARE} selected
            </span>
            
            <button
              className="flex items-center gap-1 px-3 py-1 text-sm rounded-md bg-[#F5F0FF] text-[#6D3BEB] hover:bg-[#EAE0FF]"
              onClick={() => setShowComparison(true)}
              disabled={selectedVersions.length !== 2}
            >
              <ArrowLeftRight size={14} />
              <span>Compare</span>
            </button>
            
            <button
              className="px-2 py-1 text-sm rounded-md text-[#475569] hover:bg-[#F8FAFC]"
              onClick={clearSelectedVersions}
            >
              Clear
            </button>
          </div>
        )}
      </div>
      
      <div className="border rounded-md divide-y divide-[#E2E8F0]">
        {versions.map((version) => (
          <div 
            key={version.id} 
            className={`bg-white ${isVersionSelected(version.id) ? 'bg-[#F5F0FF] border-l-4 border-l-[#6D3BEB]' : ''}`}
          >
            <div 
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-[#F8FAFC]"
              onClick={() => toggleVersionDetails(version.id)}
            >
              <div className="flex items-center">
                {/* Selection checkbox */}
                <div 
                  className="mr-3 cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleVersionSelection(version);
                  }}
                >
                  {isVersionSelected(version.id) ? (
                    <CheckCircle size={18} className="text-[#6D3BEB]" />
                  ) : (
                    <div className="w-[18px] h-[18px] border-2 border-[#CBD5E1] rounded-full hover:border-[#6D3BEB]"></div>
                  )}
                </div>
                
                <div>
                  <div className="flex items-center">
                    <span className="font-medium text-[#1E2334]">Version {version.version_number}</span>
                    <span
                      className={`ml-3 px-2 py-1 text-xs rounded-full ${
                        version.status === "draft"
                          ? "bg-yellow-100 text-yellow-800"
                          : version.status === "published"
                          ? "bg-green-100 text-green-800"
                          : version.status === "under_review"
                          ? "bg-blue-100 text-blue-800"
                          : version.status === "inactive"
                          ? "bg-gray-100 text-gray-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {version.status.charAt(0).toUpperCase() + version.status.slice(1)}
                    </span>
                  </div>
                  <div className="text-sm text-[#475569] mt-1">
                    {new Date(version.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center">
                <div className="flex space-x-2">
                  {currentVersion && currentVersion.id !== version.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        compareWithCurrent(version);
                      }}
                      className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
                    >
                      Compare with Current
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRestore(version.version_number);
                    }}
                    className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    disabled={isRestoring}
                  >
                    {isRestoring ? 'Restoring...' : 'Restore'}
                  </button>
                </div>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className={`w-5 h-5 text-[#475569] transition-transform ml-2 ${
                    expandedVersionId === version.id ? 'transform rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
            </div>
            
            {expandedVersionId === version.id && (
              <div className="p-4 bg-[#F8FAFC] border-t border-[#E2E8F0]">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-[#475569] mb-1">Name</h4>
                    <p className="text-[#1E2334]">{version.name}</p>
                  </div>
                  {version.description && (
                    <div>
                      <h4 className="text-sm font-medium text-[#475569] mb-1">Description</h4>
                      <p className="text-[#1E2334]">{version.description}</p>
                    </div>
                  )}
                </div>
                
                {(version.voice_metadata?.personality || version.voice_metadata?.tonality) && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-[#E2E8F0]">
                    {version.voice_metadata.personality && (
                      <div>
                        <h4 className="text-sm font-medium text-[#475569] mb-1">Personality</h4>
                        <p className="text-[#1E2334]">{version.voice_metadata.personality}</p>
                      </div>
                    )}
                    {version.voice_metadata.tonality && (
                      <div>
                        <h4 className="text-sm font-medium text-[#475569] mb-1">Tonality</h4>
                        <p className="text-[#1E2334]">{version.voice_metadata.tonality}</p>
                      </div>
                    )}
                  </div>
                )}
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-[#E2E8F0]">
                  <div>
                    <h4 className="text-sm font-medium text-[#475569] mb-1">Do's</h4>
                    <div className="bg-white p-3 rounded-md border border-[#E2E8F0] whitespace-pre-line">
                      {version.dos || "No do's specified"}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-[#475569] mb-1">Don'ts</h4>
                    <div className="bg-white p-3 rounded-md border border-[#E2E8F0] whitespace-pre-line">
                      {version.donts || "No don'ts specified"}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Version comparison panel */}
      {showComparison && selectedVersions.length === 2 && (
        <VersionComparisonPanel
          baseVersion={selectedVersions[0]}
          comparedVersion={selectedVersions[1]}
          onClose={() => setShowComparison(false)}
          onRestore={async (version) => {
            try {
              setIsRestoring(true);
              await brandVoiceService.restoreBrandVoiceVersion(brandVoiceId, version.version_number);
              onVersionRestore();
              setShowComparison(false);
              clearSelectedVersions();
              setError(null);
            } catch (err) {
              console.error('Failed to restore version:', err);
              setError('Failed to restore version. Please try again.');
            } finally {
              setIsRestoring(false);
            }
          }}
          onSwapVersions={swapSelectedVersions}
        />
      )}
    </div>
  );
}

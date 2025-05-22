'use client';

import { useState, useEffect } from 'react';
import { BrandVoiceVersion } from '@/lib/api/brand-voice-service';
import { brandVoiceService } from '@/lib/api/brand-voice-service';

interface VersionHistoryProps {
  brandVoiceId: string;
  onVersionRestore: () => void;
}

export function VersionHistory({ brandVoiceId, onVersionRestore }: VersionHistoryProps) {
  const [versions, setVersions] = useState<BrandVoiceVersion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRestoring, setIsRestoring] = useState(false);
  const [expandedVersionId, setExpandedVersionId] = useState<string | null>(null);

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

  const handleRestore = async (versionId: string) => {
    if (window.confirm('Are you sure you want to restore this version? This will create a new version based on the selected one.')) {
      try {
        setIsRestoring(true);
        await brandVoiceService.restoreBrandVoiceVersion(brandVoiceId, versionId);
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
      <h3 className="text-lg font-medium text-[#1E2334]">Version History</h3>
      <div className="border rounded-md divide-y divide-[#E2E8F0]">
        {versions.map((version) => (
          <div key={version.id} className="bg-white">
            <div 
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-[#F8FAFC]"
              onClick={() => toggleVersionDetails(version.id)}
            >
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
              <div className="flex items-center">
                <button
                  className="text-[#6D3BEB] hover:text-[#5A26B8] font-medium text-sm px-3 py-1 rounded-md hover:bg-[#F5F0FF] mr-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRestore(version.id);
                  }}
                  disabled={isRestoring}
                >
                  {isRestoring ? 'Restoring...' : 'Restore'}
                </button>
                <svg
                  className={`w-5 h-5 text-[#475569] transition-transform ${
                    expandedVersionId === version.id ? 'transform rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M19 9l-7 7-7-7"
                  ></path>
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
    </div>
  );
}

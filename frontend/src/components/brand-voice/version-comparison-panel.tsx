"use client";

import React, { useMemo } from 'react';
import { X, ArrowLeft, ArrowRight, RotateCcw, AlertTriangle } from 'lucide-react';
import { BrandVoiceVersion, VersionDiff } from '@/types/brand-voice';
import { BRAND_VOICE_CONFIG } from '@/config/brand-voice-config';
import { compareVersions, formatValueForDisplay, getChangeColor } from '@/utils/version-comparison';
import { cn } from '@/lib/utils';

interface VersionComparisonPanelProps {
  baseVersion: BrandVoiceVersion;
  comparedVersion: BrandVoiceVersion;
  onClose: () => void;
  onRestore: (version: BrandVoiceVersion) => void;
  onSwapVersions: () => void;
}

export function VersionComparisonPanel({
  baseVersion,
  comparedVersion,
  onClose,
  onRestore,
  onSwapVersions
}: VersionComparisonPanelProps) {
  // Generate comparison data
  const comparison = useMemo(() => 
    compareVersions(baseVersion, comparedVersion),
    [baseVersion, comparedVersion]
  );
  
  // State for confirmation dialog
  const [showRestoreConfirmation, setShowRestoreConfirmation] = React.useState(false);
  const [versionToRestore, setVersionToRestore] = React.useState<BrandVoiceVersion | null>(null);
  
  // Handle restore button click
  const handleRestoreClick = (version: BrandVoiceVersion) => {
    setVersionToRestore(version);
    setShowRestoreConfirmation(true);
  };
  
  // Handle restore confirmation
  const handleConfirmRestore = () => {
    if (versionToRestore) {
      onRestore(versionToRestore);
      setShowRestoreConfirmation(false);
    }
  };
  
  // Format date for display
  const formatDate = (dateString: string) => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Compare Versions</h2>
          <button 
            onClick={onClose}
            className="p-1 rounded-full hover:bg-gray-100 text-gray-500"
            aria-label="Close panel"
          >
            <X size={20} />
          </button>
        </div>
        
        {/* Version headers */}
        <div className="grid grid-cols-2 gap-4 px-6 py-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm text-gray-500">Version</span>
              <h3 className="font-medium">{baseVersion.version_number}</h3>
              <p className="text-sm text-gray-500">{formatDate(baseVersion.created_at)}</p>
            </div>
            <button
              onClick={() => handleRestoreClick(baseVersion)}
              className="flex items-center gap-1 px-3 py-1 text-sm rounded-md bg-primary-50 text-primary-600 hover:bg-primary-100"
              disabled={baseVersion.version_number === comparedVersion.version_number}
            >
              <RotateCcw size={14} />
              <span>Restore</span>
            </button>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm text-gray-500">Version</span>
              <h3 className="font-medium">{comparedVersion.version_number}</h3>
              <p className="text-sm text-gray-500">{formatDate(comparedVersion.created_at)}</p>
            </div>
            <button
              onClick={() => handleRestoreClick(comparedVersion)}
              className="flex items-center gap-1 px-3 py-1 text-sm rounded-md bg-primary-50 text-primary-600 hover:bg-primary-100"
              disabled={baseVersion.version_number === comparedVersion.version_number}
            >
              <RotateCcw size={14} />
              <span>Restore</span>
            </button>
          </div>
        </div>
        
        {/* Swap versions button */}
        <div className="flex justify-center -mt-4">
          <button
            onClick={onSwapVersions}
            className="bg-white border border-gray-200 rounded-full p-2 shadow-sm hover:bg-gray-50"
            aria-label="Swap versions"
          >
            <div className="flex items-center">
              <ArrowLeft size={14} className="text-gray-400" />
              <ArrowRight size={14} className="text-gray-400" />
            </div>
          </button>
        </div>
        
        {/* Comparison content */}
        <div className="overflow-y-auto flex-grow px-6 py-4">
          {comparison.differences.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-gray-500">
              <div className="bg-gray-100 rounded-full p-3 mb-3">
                <span role="img" aria-label="No differences">✓</span>
              </div>
              <p>No differences between these versions</p>
            </div>
          ) : (
            <div className="space-y-6">
              {BRAND_VOICE_CONFIG.COMPARABLE_FIELDS.map(fieldConfig => {
                const diff = comparison.differences.find(d => d.field === fieldConfig.key);
                const baseValue = formatValueForDisplay(
                  getNestedValue(baseVersion, fieldConfig.key), 
                  fieldConfig.key
                );
                const comparedValue = formatValueForDisplay(
                  getNestedValue(comparedVersion, fieldConfig.key), 
                  fieldConfig.key
                );
                
                return (
                  <div key={fieldConfig.key} className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">{fieldConfig.label}</h4>
                      <div 
                        className={cn(
                          "p-3 border rounded-md whitespace-pre-wrap",
                          diff ? `bg-${getChangeColor(diff.changeType)}` : ""
                        )}
                      >
                        {baseValue}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">{fieldConfig.label}</h4>
                      <div 
                        className={cn(
                          "p-3 border rounded-md whitespace-pre-wrap",
                          diff ? `bg-${getChangeColor(diff.changeType)}` : ""
                        )}
                      >
                        {comparedValue}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        
        {/* Restore confirmation dialog */}
        {showRestoreConfirmation && versionToRestore && (
          <div className="fixed inset-0 bg-black/50 z-60 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
              <div className="flex items-start mb-4">
                <div className="bg-amber-100 p-2 rounded-full mr-3">
                  <AlertTriangle size={20} className="text-amber-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">Restore Version {versionToRestore.version_number}?</h3>
                  <p className="text-gray-600 mt-1">
                    This will revert the brand voice to this previous version. This action cannot be undone.
                  </p>
                </div>
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowRestoreConfirmation(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmRestore}
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  Restore Version
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Helper function to get a nested value from an object
function getNestedValue(obj: any, path: string): any {
  const keys = path.split('.');
  return keys.reduce((value, key) => 
    (value && value[key] !== undefined) ? value[key] : undefined, 
    obj
  );
}

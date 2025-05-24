'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

interface ProgressIndicatorProps {
  isAnalyzing: boolean;
  analysisStage: string | null;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  isAnalyzing,
  analysisStage
}) => {
  if (!isAnalyzing) {
    return null;
  }

  const getProgressPercentage = () => {
    switch (analysisStage) {
      case 'initializing':
        return 25;
      case 'analyzing':
        return 50;
      case 'processing':
        return 75;
      case 'finalizing':
        return 90;
      case 'improving':
        return 85;
      default:
        return 10;
    }
  };

  const getStageMessage = () => {
    switch (analysisStage) {
      case 'initializing':
        return 'Initializing analysis...';
      case 'analyzing':
        return 'Analyzing content against brand voice guidelines...';
      case 'processing':
        return 'Processing analysis results...';
      case 'finalizing':
        return 'Finalizing report...';
      case 'improving':
        return 'Applying improvement to content...';
      default:
        return 'Starting analysis...';
    }
  };

  return (
    <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-md">
      <div className="flex items-center">
        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
        <div>
          <p className="font-medium">Analyzing your content...</p>
          <div className="mt-2">
            <div className="w-full bg-blue-200 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-in-out" 
                style={{ width: `${getProgressPercentage()}%` }}
              ></div>
            </div>
            <p className="text-xs mt-1">{getStageMessage()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;

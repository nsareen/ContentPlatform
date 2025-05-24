'use client';

import React from 'react';
import { Check, AlertCircle, ArrowRight } from 'lucide-react';

interface AnalysisComparisonProps {
  previousScores: {
    overall: number;
    personality: number;
    tonality: number;
    dos: number;
    donts: number;
  };
  currentScores: {
    overall: number;
    personality: number;
    tonality: number;
    dos: number;
    donts: number;
  };
  previousIssueCount: number;
  currentIssueCount: number;
  previousSuggestionCount: number;
  currentSuggestionCount: number;
}

const AnalysisComparison: React.FC<AnalysisComparisonProps> = ({
  previousScores,
  currentScores,
  previousIssueCount,
  currentIssueCount,
  previousSuggestionCount,
  currentSuggestionCount
}) => {
  // Calculate differences
  const differences = {
    overall: currentScores.overall - previousScores.overall,
    personality: currentScores.personality - previousScores.personality,
    tonality: currentScores.tonality - previousScores.tonality,
    dos: currentScores.dos - previousScores.dos,
    donts: currentScores.donts - previousScores.donts,
    issueCount: previousIssueCount - currentIssueCount, // Positive means fewer issues (improvement)
    suggestionCount: previousSuggestionCount - currentSuggestionCount // Positive means fewer suggestions (improvement)
  };

  const formatPercentage = (value: number) => {
    return (value * 100).toFixed(0) + '%';
  };

  const formatDifference = (value: number) => {
    return value > 0 ? `+${(value * 100).toFixed(0)}%` : `${(value * 100).toFixed(0)}%`;
  };

  return (
    <div className="mb-3 p-3 bg-blue-50 rounded-md">
      <h4 className="text-sm font-medium text-blue-800 mb-2">Changes from Previous Analysis</h4>
      <div className="text-xs text-blue-700">
        {differences.overall > 0 ? (
          <p className="text-green-600 flex items-center">
            <ArrowRight className="h-3 w-3 mr-1 rotate-45" />
            Overall score improved by {Math.abs((differences.overall * 100)).toFixed(0)}%
          </p>
        ) : differences.overall < 0 ? (
          <p className="text-red-600 flex items-center">
            <ArrowRight className="h-3 w-3 mr-1 rotate-135" />
            Overall score decreased by {Math.abs((differences.overall * 100)).toFixed(0)}%
          </p>
        ) : (
          <p>Overall score unchanged</p>
        )}
        
        {differences.issueCount > 0 ? (
          <p className="text-green-600 flex items-center mt-1">
            <Check className="h-3 w-3 mr-1" />
            Reduced issues by {differences.issueCount}
          </p>
        ) : differences.issueCount < 0 ? (
          <p className="text-amber-600 flex items-center mt-1">
            <AlertCircle className="h-3 w-3 mr-1" />
            New issues identified: {Math.abs(differences.issueCount)}
          </p>
        ) : (
          <p className="mt-1">Same number of issues</p>
        )}
        
        {differences.suggestionCount > 0 ? (
          <p className="text-green-600 flex items-center mt-1">
            <Check className="h-3 w-3 mr-1" />
            Reduced suggestions by {differences.suggestionCount}
          </p>
        ) : differences.suggestionCount < 0 ? (
          <p className="text-amber-600 flex items-center mt-1">
            <AlertCircle className="h-3 w-3 mr-1" />
            New suggestions added: {Math.abs(differences.suggestionCount)}
          </p>
        ) : (
          <p className="mt-1">Same number of suggestions</p>
        )}
      </div>
      
      <div className="grid grid-cols-4 gap-2 mt-3">
        <div className="text-center">
          <div className="text-xs text-gray-600">Overall</div>
          <div className="text-sm font-medium">{formatPercentage(currentScores.overall)}</div>
          <div className={`text-xs ${differences.overall > 0 ? 'text-green-600' : differences.overall < 0 ? 'text-red-600' : 'text-gray-500'}`}>
            {formatDifference(differences.overall)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-600">Personality</div>
          <div className="text-sm font-medium">{formatPercentage(currentScores.personality)}</div>
          <div className={`text-xs ${differences.personality > 0 ? 'text-green-600' : differences.personality < 0 ? 'text-red-600' : 'text-gray-500'}`}>
            {formatDifference(differences.personality)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-600">Tonality</div>
          <div className="text-sm font-medium">{formatPercentage(currentScores.tonality)}</div>
          <div className={`text-xs ${differences.tonality > 0 ? 'text-green-600' : differences.tonality < 0 ? 'text-red-600' : 'text-gray-500'}`}>
            {formatDifference(differences.tonality)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-600">Do's</div>
          <div className="text-sm font-medium">{formatPercentage(currentScores.dos)}</div>
          <div className={`text-xs ${differences.dos > 0 ? 'text-green-600' : differences.dos < 0 ? 'text-red-600' : 'text-gray-500'}`}>
            {formatDifference(differences.dos)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisComparison;

'use client';

import React from 'react';
import { Check, Wand2 } from 'lucide-react';

interface Suggestion {
  id: string;
  text: string;
}

interface SuggestionChipsProps {
  suggestions: Suggestion[];
  appliedSuggestions: Record<string, boolean>;
  onApplySuggestion: (suggestion: Suggestion) => void;
  isAnalyzing: boolean;
}

const SuggestionChips: React.FC<SuggestionChipsProps> = ({
  suggestions,
  appliedSuggestions,
  onApplySuggestion,
  isAnalyzing
}) => {
  if (suggestions.length === 0) {
    return null;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-md p-4 mb-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-md font-medium">Recommended Improvements</h3>
      </div>
      
      <div className="flex flex-wrap gap-3">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion.id}
            onClick={() => onApplySuggestion(suggestion)}
            disabled={appliedSuggestions[suggestion.id] || isAnalyzing}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors shadow-sm ${
              appliedSuggestions[suggestion.id] 
                ? 'bg-green-100 text-green-800 border border-green-300' 
                : 'bg-primary-50 text-primary-700 border border-primary-200 hover:bg-primary-100 hover:shadow'
            }`}
          >
            {appliedSuggestions[suggestion.id] ? (
              <span className="flex items-center">
                <Check size={14} className="mr-1" />
                Applied
              </span>
            ) : (
              <span className="flex items-center">
                <Wand2 size={14} className="mr-2" />
                {suggestion.text}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestionChips;

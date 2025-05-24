'use client';

import React from 'react';

interface ScoreDisplayProps {
  overall: number;
  personality: number;
  tonality: number;
  dosAlignment: number;
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
  overall,
  personality,
  tonality,
  dosAlignment
}) => {
  const formatScore = (score: number) => {
    return (score * 100).toFixed(0) + '%';
  };

  return (
    <div className="bg-white border border-gray-200 rounded-md p-4">
      <h3 className="text-md font-medium mb-3">Brand Voice Alignment Scores</h3>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-50 p-3 rounded-md">
          <div className="text-sm text-gray-500">Overall</div>
          <div className="text-xl font-semibold">{formatScore(overall)}</div>
        </div>
        <div className="bg-gray-50 p-3 rounded-md">
          <div className="text-sm text-gray-500">Personality</div>
          <div className="text-xl font-semibold">{formatScore(personality)}</div>
        </div>
        <div className="bg-gray-50 p-3 rounded-md">
          <div className="text-sm text-gray-500">Tonality</div>
          <div className="text-xl font-semibold">{formatScore(tonality)}</div>
        </div>
        <div className="bg-gray-50 p-3 rounded-md">
          <div className="text-sm text-gray-500">Do's Alignment</div>
          <div className="text-xl font-semibold">{formatScore(dosAlignment)}</div>
        </div>
      </div>
    </div>
  );
};

export default ScoreDisplay;

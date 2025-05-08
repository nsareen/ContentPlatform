"use client";

import { useState } from 'react';
import RichPlaygroundPanel from '@/components/brand-voice/rich-playground-panel-v2';

export default function TestFixedPanelPage() {
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Test Fixed Rich Playground Panel</h1>
        
        <p className="mb-4">
          This page tests the fixed version of the Rich Playground Panel component that addresses image loading issues.
        </p>
        
        <button
          onClick={() => setIsPanelOpen(true)}
          className="bg-[#6D3BEB] text-white py-2 px-4 rounded-md hover:bg-[#5B32C7] focus:outline-none focus:ring-2 focus:ring-[#6D3BEB] focus:ring-offset-2"
        >
          Open Rich Playground Panel
        </button>
        
        {isPanelOpen && (
          <RichPlaygroundPanel
            isOpen={isPanelOpen}
            brandVoiceId="test-brand-voice-id"
            brandVoiceName="Test Brand Voice"
            onClose={() => setIsPanelOpen(false)}
          />
        )}
      </div>
    </div>
  );
}

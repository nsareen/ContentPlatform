"use client";

import React, { useEffect } from 'react';
import { RichPlaygroundPanel } from '@/components/brand-voice/rich-playground-panel';

export default function TestRichMediaPage() {
  // Set the dev token in localStorage on component mount
  useEffect(() => {
    // Only run on client side
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        // Set the dev token from our API
        fetch('http://localhost:8000/api/dev-token')
          .then(res => res.json())
          .then(data => {
            localStorage.setItem('auth_token', data.access_token);
            console.log('Dev token set in localStorage');
          })
          .catch(err => {
            console.error('Error fetching dev token:', err);
          });
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold mb-6">Rich Media Playground Test Page</h1>
      <p className="mb-4">This page allows you to test the Rich Media Playground Panel directly.</p>
      
      <div className="flex justify-center">
        <button 
          className="bg-[#6D3BEB] hover:bg-[#5A26B8] text-white px-6 py-3 rounded-md"
          onClick={() => {
            // Force the RichPlaygroundPanel to be visible
            const richPlaygroundPanel = document.getElementById('rich-playground-panel');
            if (richPlaygroundPanel) {
              richPlaygroundPanel.classList.remove('hidden');
            }
          }}
        >
          Open Rich Media Playground
        </button>
      </div>
      
      {/* Always render the RichPlaygroundPanel but initially hidden */}
      <div id="rich-playground-panel" className="hidden">
        <RichPlaygroundPanel 
          isOpen={true} 
          onClose={() => {
            const richPlaygroundPanel = document.getElementById('rich-playground-panel');
            if (richPlaygroundPanel) {
              richPlaygroundPanel.classList.add('hidden');
            }
          }}
          brandVoiceId="test-brand-voice"
          brandVoiceName="Test Brand Voice"
        />
      </div>
    </div>
  );
}

"use client";

import React, { useState } from 'react';
import { X, Send, Loader2, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PlaygroundPanelProps {
  isOpen: boolean;
  onClose: () => void;
  brandVoiceId?: string;
  brandVoiceName?: string;
}

export function PlaygroundPanel({ isOpen, onClose, brandVoiceId, brandVoiceName }: PlaygroundPanelProps) {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted with prompt:', prompt);
    if (!prompt.trim() || isGenerating) return;
    
    try {
      setIsGenerating(true);
      setGeneratedContent('');
      
      // Get the authentication token
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('Authentication token not found. Please log in again.');
      }
      
      // Call the agent API to generate content
      const response = await fetch('http://localhost:8000/api/agent/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          brand_voice_id: brandVoiceId,
          prompt: prompt,
          content_type: 'general'
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to generate content');
      }
      
      const responseData = await response.json();
      console.log('Content generated successfully:', responseData);
      
      // Get the generated content from the response
      const generatedText = responseData.result?.content || 'No content was generated.';
      
      // Simulate streaming by adding one character at a time
      for (let i = 0; i < generatedText.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 15));
        setGeneratedContent(prev => prev + generatedText[i]);
      }
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  const handleCopyContent = () => {
    if (generatedContent) {
      navigator.clipboard.writeText(generatedContent);
      // Could add a toast notification here
    }
  };

  return (
    <div 
      className={cn(
        "fixed top-0 right-0 z-50 h-screen w-96 bg-white shadow-lg transform transition-transform duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "translate-x-full"
      )}
      style={{ paddingTop: '56px' }} // Account for the header height
    >
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-medium">
            {brandVoiceName ? `${brandVoiceName} Playground` : 'Brand Voice Playground'}
          </h2>
          <button 
            onClick={onClose}
            className="p-1 rounded-full hover:bg-gray-100 text-gray-500"
            aria-label="Close panel"
          >
            <X size={20} />
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Instructions */}
          <div className="bg-primary-50 p-3 rounded-md text-sm text-primary-800">
            <p>Enter a prompt to generate content that follows the brand voice guidelines.</p>
          </div>
          
          {/* Generated content display */}
          {generatedContent && (
            <div className="bg-white border border-gray-200 rounded-md p-4 relative">
              <div className="prose prose-sm max-w-none">
                <p>{generatedContent}</p>
              </div>
              
              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <button 
                    onClick={handleCopyContent}
                    className="p-1 rounded-md hover:bg-gray-100 text-gray-500"
                    aria-label="Copy content"
                  >
                    <Copy size={16} />
                  </button>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button className="p-1 rounded-md hover:bg-gray-100 text-gray-500">
                    <ThumbsUp size={16} />
                  </button>
                  <button className="p-1 rounded-md hover:bg-gray-100 text-gray-500">
                    <ThumbsDown size={16} />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Input form */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your prompt here..."
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-[#6D3BEB] focus:border-[#6D3BEB] resize-none"
              rows={3}
              disabled={isGenerating}
            />
            
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={!prompt.trim() || isGenerating}
                className={cn(
                  "flex items-center justify-center w-full px-6 py-3 rounded-md text-white font-medium shadow-sm text-lg",
                  !prompt.trim() || isGenerating 
                    ? "bg-gray-300 cursor-not-allowed" 
                    : "bg-[#6D3BEB] hover:bg-[#5A26B8] transition-colors"
                )}
                onClick={handleSubmit}
              >
                {isGenerating ? (
                  <>
                    <Loader2 size={18} className="animate-spin mr-2" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Send size={18} className="mr-2" />
                    <span>Generate</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

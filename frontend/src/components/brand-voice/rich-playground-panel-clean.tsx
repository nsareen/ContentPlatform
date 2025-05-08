"use client";

import React, { useState } from 'react';
import { X, FileText, Image, Loader2, ZoomIn } from 'lucide-react';

interface RichPlaygroundPanelProps {
  brandVoiceId?: string;
  brandVoiceName?: string;
  onClose: () => void;
  isOpen?: boolean;
}

interface RichContentImage {
  url: string;
  description?: string;
  model?: string;
}

// Simple Image Modal component for viewing full-size images
function ImageModal({ 
  isOpen, 
  imageUrl, 
  imageDescription, 
  onClose 
}: { 
  isOpen: boolean; 
  imageUrl: string; 
  imageDescription?: string; 
  onClose: () => void;
}) {
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black/80 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="relative max-w-4xl max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <button 
          className="absolute top-2 right-2 bg-black/50 text-white p-1 rounded-full hover:bg-black/70 z-10"
          onClick={onClose}
        >
          <X size={20} />
        </button>
        <img 
          src={imageUrl} 
          alt={imageDescription || 'Full size image'} 
          className="max-w-full max-h-[85vh] object-contain rounded-md"
        />
        {imageDescription && (
          <div className="bg-black/70 p-3 text-white text-sm">
            {imageDescription}
          </div>
        )}
      </div>
    </div>
  );
}

export function RichPlaygroundPanel({ 
  brandVoiceId = "", 
  brandVoiceName = "Brand", 
  onClose,
  isOpen = true
}: RichPlaygroundPanelProps) {
  // State for the form
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('flyer');
  
  // State for the generated content
  const [generatedContent, setGeneratedContent] = useState('');
  const [generatedImages, setGeneratedImages] = useState<RichContentImage[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  // State for the image modal
  const [selectedImage, setSelectedImage] = useState<RichContentImage | null>(null);
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);
  
  // Function to open the image modal
  const openImageModal = (image: RichContentImage) => {
    setSelectedImage(image);
    setIsImageModalOpen(true);
  };
  
  // Function to close the image modal
  const closeImageModal = () => {
    setIsImageModalOpen(false);
  };
  
  // Function to handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      alert("Please enter a prompt to generate content.");
      return;
    }
    
    setIsGenerating(true);
    setGeneratedContent('');
    setGeneratedImages([]);
    setError(null);
    
    try {
      // Simulate API call for testing
      setTimeout(() => {
        // Mock response data
        const mockContent = `Here's a sample flyer for ${brandVoiceName || 'your brand'}:\n\n**SUMMER SALE**\n\nDiscover amazing deals on our latest products. Limited time offer!`;
        
        // Mock image data
        const mockImages: RichContentImage[] = [
          {
            url: 'https://placehold.co/800x600/6D3BEB/FFFFFF?text=Sample+Image+1',
            description: 'A promotional image for the summer sale featuring bright colors and product displays'
          },
          {
            url: 'https://placehold.co/800x600/3B82F6/FFFFFF?text=Sample+Image+2',
            description: 'A lifestyle image showing people enjoying the products during summer'
          }
        ];
        
        setGeneratedContent(mockContent);
        setGeneratedImages(mockImages);
        setIsGenerating(false);
      }, 2000);
    } catch (error) {
      setError('An error occurred while generating content. Please try again.');
      setIsGenerating(false);
    }
  };
  
  // If isOpen is false, don't render anything
  if (isOpen === false) {
    return null;
  }
  
  return (
    <>
      {/* Image Modal */}
      {selectedImage && (
        <ImageModal
          isOpen={isImageModalOpen}
          imageUrl={selectedImage.url}
          imageDescription={selectedImage.description}
          onClose={closeImageModal}
        />
      )}
      
      <div className="fixed inset-y-0 right-0 w-full sm:w-[450px] bg-white shadow-xl flex flex-col z-50 overflow-hidden">
        <div className="flex flex-col h-full">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-medium">{brandVoiceName || 'Brand'} Rich Media</h2>
            <button 
              className="p-1 rounded-full hover:bg-gray-100 text-gray-500"
              onClick={onClose}
              aria-label="Close panel"
            >
              <X size={20} />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Content type selection */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Content Type</label>
              <select 
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md"
                disabled={isGenerating}
              >
                <option value="flyer">Product Flyer</option>
                <option value="social-post">Social Media Post</option>
                <option value="email-campaign">Email Campaign</option>
                <option value="product-launch">Product Launch Announcement</option>
              </select>
            </div>
            
            {/* Generated content display */}
            {generatedContent && (
              <div className="bg-white border border-gray-200 rounded-md p-4 relative space-y-4">
                {/* Text content */}
                <div className="prose prose-sm max-w-none">
                  <h3 className="flex items-center text-sm font-medium text-gray-700 mb-2">
                    <FileText size={16} className="mr-1" /> Text Content
                  </h3>
                  <p className="whitespace-pre-line">{generatedContent}</p>
                </div>
                
                {/* Images */}
                {generatedImages.length > 0 && (
                  <div className="mt-4">
                    <h3 className="flex items-center text-sm font-medium text-gray-700 mb-2">
                      <Image size={16} className="mr-1" /> Generated Images ({generatedImages.length})
                    </h3>
                    
                    <div className="grid grid-cols-2 gap-3 mt-2">
                      {generatedImages.map((image, index) => (
                        <div 
                          key={`image-${index}`}
                          className="relative border border-gray-200 rounded-md overflow-hidden cursor-pointer group"
                          onClick={() => openImageModal(image)}
                        >
                          {/* Thumbnail container with fixed height */}
                          <div className="h-40 relative">
                            <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-0">
                              <div id={`loading-${index}`} className="animate-pulse flex items-center justify-center">
                                <Loader2 size={24} className="animate-spin text-gray-400" />
                              </div>
                            </div>
                            
                            <img 
                              src={image.url}
                              alt={image.description || `Generated image ${index + 1}`}
                              className="w-full h-full object-cover relative z-5"
                              onLoad={(e) => {
                                // Hide loading indicator
                                const loadingEl = document.getElementById(`loading-${index}`);
                                if (loadingEl) loadingEl.style.display = 'none';
                                // Show the image
                                e.currentTarget.style.opacity = '1';
                              }}
                              onError={(e) => {
                                // If image fails to load, use a placeholder
                                e.currentTarget.src = `https://placehold.co/600x600/6D3BEB/FFFFFF?text=Image+Unavailable`;
                                // Hide loading indicator
                                const loadingEl = document.getElementById(`loading-${index}`);
                                if (loadingEl) loadingEl.style.display = 'none';
                              }}
                              style={{ opacity: 0 }}
                            />
                            
                            {/* Zoom indicator overlay on hover */}
                            <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity z-10">
                              <div className="bg-white/90 rounded-full p-1">
                                <ZoomIn size={20} className="text-gray-700" />
                              </div>
                            </div>
                          </div>
                          
                          {/* Image description */}
                          {image.description && (
                            <div className="bg-gray-100 p-2 text-xs text-gray-700 line-clamp-2">
                              {image.description}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {/* Error message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-md text-sm">
                {error}
              </div>
            )}
          </div>
          
          {/* Input form */}
          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
              <div className="flex-1">
                <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">
                  Prompt
                </label>
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder={`Describe what you want to generate for ${brandVoiceName || 'your brand'}...`}
                  className="w-full p-2 border border-gray-300 rounded-md min-h-[100px]"
                  disabled={isGenerating}
                />
              </div>
              
              <button
                type="submit"
                disabled={isGenerating || !prompt.trim()}
                className="w-full bg-[#6D3BEB] text-white py-2 px-4 rounded-md hover:bg-[#5B32C7] focus:outline-none focus:ring-2 focus:ring-[#6D3BEB] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isGenerating ? (
                  <>
                    <Loader2 size={18} className="animate-spin mr-2" />
                    Generating...
                  </>
                ) : (
                  'Generate'
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}

// Default export
export default RichPlaygroundPanel;

"use client";

import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2, ZoomIn, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RichPlaygroundPanelProps {
  isOpen: boolean;
  onClose: () => void;
  brandVoiceId?: string;
  brandVoiceName?: string;
}

interface RichContentImage {
  url: string;
  description?: string;
  model?: string;
}

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'info';
  id: string;
}

// Toast notification component
function Toast({ message, type, id }: ToastProps) {
  return (
    <div 
      id={id}
      className={cn(
        "fixed bottom-4 right-4 p-4 rounded-md shadow-md z-50 flex items-center space-x-2 max-w-md",
        type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' : 
        type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 
        'bg-blue-100 text-blue-800 border border-blue-200'
      )}
    >
      {type === 'error' && <AlertCircle size={18} />}
      <span>{message}</span>
    </div>
  );
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

// Custom toast hook
function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([]);
  
  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = `toast-${Date.now()}`;
    setToasts(prev => [...prev, { message, type, id }]);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 5000);
    
    return id;
  };
  
  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };
  
  return {
    toasts,
    showToast,
    removeToast
  };
}

// Function to check if backend is available
async function checkBackendAvailability(): Promise<boolean> {
  try {
    const response = await fetch('http://localhost:8000/api/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.ok;
  } catch (error) {
    console.error('Backend availability check failed:', error);
    return false;
  }
}

// Function to preload an image and check if it's valid
async function preloadImage(url: string): Promise<boolean> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = url;
  });
}

// Function to get a proxied image URL to prevent caching issues
function getProxiedImageUrl(originalUrl: string): string {
  const timestamp = Date.now();
  return `http://localhost:8000/api/proxy/image?url=${encodeURIComponent(originalUrl)}&t=${timestamp}`;
}

export function RichPlaygroundPanel({ 
  brandVoiceId = "", 
  brandVoiceName = "Brand", 
  onClose,
  isOpen = true
}: RichPlaygroundPanelProps) {
  // Toast state
  const { toasts, showToast, removeToast } = useToast();
  
  // State for the form
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('flyer');
  
  // State for the generated content
  const [generatedContent, setGeneratedContent] = useState('');
  const [generatedImages, setGeneratedImages] = useState<RichContentImage[]>([]);
  
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
      showToast('Please enter a prompt', 'error');
      return;
    }
    
    const backendAvailable = await checkBackendAvailability();
    if (!backendAvailable) {
      showToast('Backend service is not available. Please try again later.', 'error');
      return;
    }
    
    setIsGenerating(true);
    setGeneratedContent('');
    setGeneratedImages([]);
    
    try {
      // Prepare the request body
      const requestBody = {
        prompt: prompt,
        brand_voice_id: brandVoiceId || undefined,
        content_type: selectedTemplate,
        image_model: 'dall-e-3',
        image_quality: 'standard',
        image_size: '1024x1024',
        image_style: 'natural'
      };
      
      // Make the API call to the backend
      const response = await fetch('http://localhost:8000/api/rich-content/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success' && data.result) {
        // Set the generated content
        setGeneratedContent(data.result.text_content || '');
        
        // Process and validate images
        const images = data.result.images || [];
        const validatedImages: RichContentImage[] = [];
        
        for (const image of images) {
          if (image.url) {
            // Check if the image is valid
            const isValid = await preloadImage(image.url);
            if (isValid) {
              validatedImages.push({
                url: image.url,
                description: image.description || '',
                model: image.model || 'dall-e-3'
              });
            }
          }
        }
        
        setGeneratedImages(validatedImages);
        
        if (validatedImages.length === 0 && images.length > 0) {
          showToast('Images were generated but could not be loaded', 'info');
        }
      } else if (data.status === 'error') {
        showToast(data.message || 'An error occurred while generating content', 'error');
      }
    } catch (err) {
      console.error('Error generating content:', err);
      showToast('An error occurred while generating content. Please try again.', 'error');
    } finally {
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
      {selectedImage && isImageModalOpen && (
        <ImageModal
          isOpen={isImageModalOpen}
          imageUrl={selectedImage.url}
          imageDescription={selectedImage.description}
          onClose={closeImageModal}
        />
      )}
      
      {/* Toast notifications */}
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          message={toast.message}
          type={toast.type}
        />
      ))}
      
      {/* Panel */}
      <div className="fixed inset-y-0 right-0 w-[450px] bg-white shadow-xl z-30 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 p-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Rich Content Playground
            {brandVoiceName && ` - ${brandVoiceName}`}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 focus:outline-none"
          >
            <X size={20} />
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {/* Generated content */}
          {isGenerating ? (
            <div className="flex flex-col items-center justify-center h-full">
              <Loader2 size={40} className="text-primary animate-spin mb-4" />
              <p className="text-gray-600">Generating content...</p>
            </div>
          ) : (
            <div className="space-y-6">
              {generatedContent && (
                <div className="bg-gray-50 p-4 rounded-md">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Generated Text</h3>
                  <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                    {generatedContent}
                  </div>
                </div>
              )}
              
              {generatedImages.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-sm font-medium text-gray-700">Generated Images</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {generatedImages.map((image, index) => (
                      <div 
                        key={`image-${index}`} 
                        className="border border-gray-200 rounded-md overflow-hidden flex flex-col"
                      >
                        {/* Image container with fixed height */}
                        <div 
                          className="relative h-40 cursor-pointer group"
                          onClick={() => openImageModal(image)}
                        >
                          {/* Loading indicator */}
                          <div id={`loading-${index}`} className="absolute inset-0 flex items-center justify-center bg-gray-100">
                            <Loader2 size={24} className="text-gray-400 animate-spin" />
                          </div>
                          
                          {/* Actual image */}
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

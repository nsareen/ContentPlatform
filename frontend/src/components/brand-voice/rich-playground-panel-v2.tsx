"use client";

import React, { useState } from 'react';
import { X, Loader2, ZoomIn, AlertCircle } from 'lucide-react';

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
      <div className="relative max-w-4xl max-h-[90vh] overflow-hidden" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
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

// Toast notification component
function Toast({ message, type }: { message: string; type: 'success' | 'error' | 'info' }) {
  return (
    <div 
      className={`fixed bottom-4 right-4 p-4 rounded-md shadow-md z-50 flex items-center space-x-2 max-w-md
        ${type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' : 
          type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 
          'bg-blue-100 text-blue-800 border border-blue-200'}`}
    >
      {type === 'error' && <AlertCircle size={18} />}
      <span>{message}</span>
    </div>
  );
}

// Function to get auth token from localStorage or try to get a dev token
async function getAuthToken(): Promise<string | null> {
  // Check if we already have a token
  const existingToken = localStorage.getItem('token');
  if (existingToken) {
    return existingToken;
  }
  
  // Try to get a dev token
  try {
    console.log('No auth token found, attempting to get dev token');
    const tokenResponse = await fetch('http://localhost:8000/api/dev-token', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (tokenResponse.ok) {
      const tokenData = await tokenResponse.json();
      localStorage.setItem('token', tokenData.access_token);
      console.log('Successfully obtained dev token');
      return tokenData.access_token;
    } else {
      console.warn('Failed to get dev token, API calls requiring auth will fail');
      return null;
    }
  } catch (err) {
    console.error('Error getting dev token:', err);
    return null;
  }
}

// Function to check if backend is available
async function checkBackendAvailability(): Promise<boolean> {
  try {
    // Try to access the root endpoint which doesn't require auth
    const response = await fetch('http://localhost:8000/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response.ok;
  } catch (err) {
    console.error('Backend availability check failed:', err);
    return false;
  }
}

// Function to preload an image and check if it's valid
async function preloadImage(url: string): Promise<boolean> {
  console.log(`Preloading image: ${url.substring(0, 50)}...`);
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      console.log(`Image loaded successfully: ${url.substring(0, 50)}...`);
      resolve(true);
    };
    img.onerror = (error) => {
      console.error(`Image failed to load: ${url.substring(0, 50)}...`, error);
      resolve(false);
    };
    img.src = url;
  });
}

export function RichPlaygroundPanel({ 
  brandVoiceId = "", 
  brandVoiceName = "Brand", 
  onClose,
  isOpen = false
}: RichPlaygroundPanelProps) {
  // State for the form
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error' | 'info'} | null>(null);
  
  // State for generated content
  const [generatedContent, setGeneratedContent] = useState<string>('');
  const [generatedImages, setGeneratedImages] = useState<RichContentImage[]>([]);
  
  // State for API response data
  const [apiResponseData, setApiResponseData] = useState<any>(null);
  
  // State for image modal
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState<RichContentImage | null>(null);
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);
  
  
  // Function to show a toast notification
  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type });
    
    // Auto hide after 5 seconds
    setTimeout(() => {
      setToast(null);
    }, 5000);
  };
  
  // Function to handle image click
  const handleImageClick = (image: RichContentImage) => {
    setSelectedImage(image);
    setIsImageModalOpen(true);
  };
  
  // Function to close the image modal
  const closeImageModal = () => {
    setIsImageModalOpen(false);
  };
  
  // Function to generate content
  const handleGenerateContent = async () => {
    if (!prompt) {
      showToast('Please enter a prompt', 'error');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Check if backend is available
      const isBackendAvailable = await checkBackendAvailability();
      if (!isBackendAvailable) {
        throw new Error('Backend service is not available');
      }

      // Get auth token if needed
      const token = await getAuthToken();
      if (!token) {
        throw new Error('Failed to get authentication token');
      }

      // Make API request to generate content
      console.log('Sending request to rich content generation API with token:', token.substring(0, 10) + '...');
      const response = await fetch('http://localhost:8000/api/rich-content/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prompt,
          content_type: 'flyer',
          brand_voice_id: brandVoiceId || undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API error:', errorData);
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Generated content:', data);

      // Extract text content
      const textContent = data.result.text_content || '';
      
      // Extract images
      const images = data.result.images || [];
      console.log('Images from API:', images);
      
      // Log image descriptions for debugging
      console.log('Image descriptions from API:', data.result.image_descriptions || []);
      
      // If we have image descriptions but no images, check if there's an error message
      if ((data.result.image_descriptions?.length > 0) && images.length === 0) {
        console.warn('Image descriptions found but no images were generated');
        if (data.result.image_generation_error) {
          console.error('Image generation error:', data.result.image_generation_error);
          setError(`Image generation failed: ${data.result.image_generation_error}`);
        }
      }

      // Validate images
      const validatedImages: RichContentImage[] = [];
      for (const image of images) {
        if (image.url) {
          try {
            console.log(`Validating image URL: ${image.url.substring(0, 50)}...`);
            const isValid = await preloadImage(image.url);
            if (isValid) {
              console.log('Image validated successfully');
              validatedImages.push(image);
            } else {
              console.error('Image failed validation check');
            }
          } catch (imgErr) {
            console.error('Error validating image:', imgErr);
          }
        } else {
          console.warn('Image object missing URL property:', image);
        }
      }

      // Store the full API response data
      setApiResponseData(data);
      
      // Update state with generated content
      setGeneratedContent(textContent);
      setGeneratedImages(validatedImages);
      setIsLoading(false);
    } catch (err) {
      console.error('Error generating content:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setIsLoading(false);
    }
  };

  // If isOpen is false, don't render anything
  if (!isOpen) {
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
      
      {/* Toast notification */}
      {toast && <Toast message={toast.message} type={toast.type} />}
      
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
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-full">
              <Loader2 size={40} className="text-primary animate-spin mb-4" />
              <p className="text-gray-600">Generating content...</p>
            </div>
          ) : error ? (
            <div className="p-4 border border-red-300 bg-red-50 rounded-md">
              <div className="flex items-center gap-2">
                <AlertCircle size={16} className="text-red-500" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          ) : (
            generatedContent ? (
              <>
                <div className="whitespace-pre-wrap">{generatedContent}</div>
                
                {generatedImages.length > 0 ? (
                  <div className="mt-6">
                    <h3 className="text-lg font-semibold mb-2">Generated Images</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {generatedImages.map((image, index) => (
                        <div key={index} className="relative border rounded-md overflow-hidden">
                          <img 
                            src={image.url} 
                            alt={image.description || `Generated image ${index + 1}`}
                            className="w-full h-auto cursor-pointer"
                            onClick={() => handleImageClick(image)}
                          />
                          <button 
                            className="absolute top-2 right-2 bg-black bg-opacity-50 rounded-full p-1"
                            onClick={() => handleImageClick(image)}
                          >
                            <ZoomIn size={16} className="text-white" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="mt-6 p-4 border border-yellow-300 bg-yellow-50 rounded-md">
                    <div className="flex items-center gap-2">
                      <AlertCircle size={16} className="text-yellow-500" />
                      <div className="text-sm">
                        <p>No images were generated. {error ? error : 'Check if the OpenAI API key is configured correctly.'}</p>
                        {apiResponseData?.result?.image_descriptions?.length > 0 && (
                          <div className="mt-2">
                            <p className="font-semibold">Image descriptions that were attempted:</p>
                            <ul className="list-disc pl-5 mt-1 space-y-1">
                              {apiResponseData.result.image_descriptions.map((desc: string, i: number) => (
                                <li key={i} className="text-xs">{desc.substring(0, 100)}{desc.length > 100 ? '...' : ''}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {apiResponseData?.result?.image_generation_error && (
                          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                            <p className="text-xs text-red-700">{apiResponseData.result.image_generation_error}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center text-gray-500 mt-8">
                Enter a prompt and click "Generate" to create content
              </div>
            )
          )}
        </div>
        
        {/* Input form */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={(e: React.FormEvent) => { e.preventDefault(); handleGenerateContent(); }} className="flex flex-col space-y-4">
            <div className="flex-1">
              <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">
                Prompt
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
                placeholder={`Describe what you want to generate for ${brandVoiceName || 'your brand'}...`}
                className="w-full p-2 border border-gray-300 rounded-md min-h-[100px]"
                disabled={isLoading}
              />
            </div>
            
            <button
              type="submit"
              disabled={isLoading || !prompt.trim()}
              className="w-full bg-[#6D3BEB] text-white py-2 px-4 rounded-md hover:bg-[#5B32C7] focus:outline-none focus:ring-2 focus:ring-[#6D3BEB] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? (
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
    </>
  );
}

export default RichPlaygroundPanel;

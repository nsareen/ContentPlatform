'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, AlertCircle, ImageIcon } from 'lucide-react';
import { richContentService } from '@/lib/api/rich-content-service';

export default function TestRichContentPage() {
  const [prompt, setPrompt] = useState('Create a promotional image for a coffee shop with a steaming cup of coffee and pastries');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [images, setImages] = useState<any[]>([]);

  // Function to get a proxied image URL
  const getProxiedImageUrl = (originalUrl: string): string => {
    // Add a timestamp to prevent caching
    const timestamp = Date.now();
    return `http://localhost:8000/api/proxy/image?url=${encodeURIComponent(originalUrl)}&t=${timestamp}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    
    setIsLoading(true);
    setResponse(null);
    setImages([]);
    setError(null);
    
    try {
      console.log('Generating rich content with prompt:', prompt);
      
      // Call the rich content service
      const responseData = await richContentService.generateRichContent({
        prompt: prompt,
        content_type: 'flyer',
        image_quality: 'standard',
        image_style: 'natural'
      });
      
      console.log('Rich content response:', responseData);
      setResponse(responseData);
      
      // Check for images in the response
      if (responseData.result && responseData.result.images && responseData.result.images.length > 0) {
        console.log('Found images in response:', responseData.result.images);
        setImages(responseData.result.images);
      } else {
        console.log('No images found in response');
      }
    } catch (err) {
      console.error('Error generating rich content:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Rich Content Generation Test</h1>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Generate Rich Content</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your prompt here..."
              className="min-h-[100px]"
            />
            
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : 'Generate Rich Content'}
            </Button>
          </form>
          
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md flex items-start">
              <AlertCircle className="text-red-500 mr-2 flex-shrink-0" size={18} />
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>
      
      {response && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>API Response</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium mb-1">Status:</h3>
                <p className="text-sm">{response.status}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium mb-1">Action:</h3>
                <p className="text-sm">{response.action}</p>
              </div>
              
              {response.result && response.result.text_content && (
                <div>
                  <h3 className="text-sm font-medium mb-1">Text Content:</h3>
                  <div className="p-3 bg-gray-50 rounded-md">
                    <p className="text-sm whitespace-pre-line">{response.result.text_content}</p>
                  </div>
                </div>
              )}
              
              {response.message && (
                <div>
                  <h3 className="text-sm font-medium mb-1">Message:</h3>
                  <div className="p-3 bg-gray-50 rounded-md">
                    <p className="text-sm whitespace-pre-line">{response.message}</p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
      
      {images.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Images</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 grid-cols-1">
              {images.map((image, index) => (
                <div key={index} className="space-y-2 border border-gray-200 rounded-md p-4">
                  <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden">
                    {image.url ? (
                      <div className="relative">
                        {/* Loading indicator */}
                        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10" id={`loading-${index}`}>
                          <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                        </div>
                        
                        <img 
                          src={getProxiedImageUrl(image.url)}
                          alt={image.description || `Generated image ${index + 1}`}
                          className="w-full h-full object-contain relative z-5"
                          style={{ opacity: 0 }}
                          onLoad={(e: React.SyntheticEvent<HTMLImageElement, Event>) => {
                            console.log(`Image ${index + 1} loaded successfully via proxy`);
                            // Hide loading indicator
                            const loadingEl = document.getElementById(`loading-${index}`);
                            if (loadingEl) loadingEl.style.display = 'none';
                            // Show the image
                            e.currentTarget.style.opacity = '1';
                          }}
                          onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => {
                            console.error(`Error loading image via proxy: ${image.url}`);
                            
                            // Try direct URL as fallback
                            console.log("Trying direct URL as fallback...");
                            e.currentTarget.src = image.url;
                            
                            // If direct URL also fails, use a placeholder
                            e.currentTarget.onerror = () => {
                              console.error("Direct URL also failed, using placeholder");
                              e.currentTarget.src = 'https://placehold.co/600x400/png?text=Image+Not+Available';
                              
                              // Show the image anyway
                              e.currentTarget.style.opacity = '1';
                            };
                            
                            // Show the image
                            e.currentTarget.style.opacity = '1';
                            
                            // Hide loading indicator
                            const loadingEl = document.getElementById(`loading-${index}`);
                            if (loadingEl) loadingEl.style.display = 'none';
                          }}
                          crossOrigin="anonymous"
                        />
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-full bg-gray-100 p-4">
                        <div className="text-center">
                          <ImageIcon size={24} className="mx-auto mb-2 text-gray-400" />
                          <p className="text-sm text-gray-500">No image available</p>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {image.description && (
                    <p className="text-sm text-gray-600">{image.description}</p>
                  )}
                  
                  {image.model && (
                    <p className="text-xs text-gray-500">Model: {image.model}</p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, AlertCircle } from 'lucide-react';

export default function TestProxySimplePage() {
  const [imageUrl, setImageUrl] = useState('https://picsum.photos/800/600');
  const [proxyUrl, setProxyUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Function to get a proxied image URL
  const getProxiedImageUrl = (originalUrl: string): string => {
    // Add a timestamp to prevent caching
    const timestamp = Date.now();
    return `http://localhost:8000/api/proxy/image?url=${encodeURIComponent(originalUrl)}&t=${timestamp}`;
  };

  const handleTestProxy = () => {
    if (!imageUrl.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    // Generate the proxy URL
    const newProxyUrl = getProxiedImageUrl(imageUrl);
    setProxyUrl(newProxyUrl);
    
    console.log('Original URL:', imageUrl);
    console.log('Proxy URL:', newProxyUrl);
  };

  const handleImageLoad = () => {
    setIsLoading(false);
    console.log('Image loaded successfully!');
  };

  const handleImageError = () => {
    setIsLoading(false);
    setError('Failed to load image through proxy');
    console.error('Image failed to load through proxy');
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Simple Image Proxy Test</h1>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Test Image Proxy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-2">
              <Input
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="Enter image URL to test"
                className="flex-1"
              />
              <Button onClick={handleTestProxy}>
                Test Proxy
              </Button>
            </div>
            
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md flex items-start">
                <AlertCircle className="text-red-500 mr-2 flex-shrink-0" size={18} />
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
            
            {proxyUrl && (
              <div className="border border-gray-200 rounded-md p-4">
                <h3 className="text-sm font-medium mb-2">Proxy URL:</h3>
                <p className="text-xs text-gray-600 break-all mb-4">{proxyUrl}</p>
                
                <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden">
                  {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-10">
                      <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
                    </div>
                  )}
                  
                  <img
                    src={proxyUrl}
                    alt="Proxied image"
                    className="w-full h-full object-contain"
                    onLoad={handleImageLoad}
                    onError={handleImageError}
                  />
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Direct Image (No Proxy)</h2>
        {imageUrl && (
          <div className="border border-gray-200 rounded-md p-4">
            <div className="aspect-video bg-gray-100 rounded-md overflow-hidden">
              <img
                src={imageUrl}
                alt="Direct image (no proxy)"
                className="w-full h-full object-contain"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';

export default function TestImageProxy() {
  const [imageUrl, setImageUrl] = useState('');
  const [proxyUrl, setProxyUrl] = useState('');
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const testProxy = async () => {
    if (!imageUrl) return;
    
    setIsLoading(true);
    setStatus('Testing proxy...');
    
    try {
      // Create the proxy URL
      const encodedUrl = encodeURIComponent(imageUrl);
      const proxy = `http://localhost:8000/api/proxy/image?url=${encodedUrl}`;
      setProxyUrl(proxy);
      
      // Test the proxy with a HEAD request
      const response = await fetch(proxy, { method: 'HEAD' });
      setStatus(`Proxy status: ${response.status} ${response.statusText}`);
      
      console.log('Proxy response headers:', response.headers);
      const contentType = response.headers.get('content-type');
      if (contentType) {
        setStatus(prev => `${prev}, Content-Type: ${contentType}`);
      }
    } catch (error) {
      console.error('Error testing proxy:', error);
      setStatus(`Error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Image Proxy Tester</h1>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Test Image Proxy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input
              placeholder="Enter image URL to test"
              value={imageUrl}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setImageUrl(e.target.value)}
              className="flex-1"
            />
            <Button onClick={testProxy} disabled={isLoading}>
              {isLoading ? 'Testing...' : 'Test Proxy'}
            </Button>
          </div>
          
          {status && (
            <div className="mb-4 p-2 bg-gray-100 rounded">
              <p className="font-mono text-sm">{status}</p>
            </div>
          )}
          
          {proxyUrl && (
            <div className="mb-4">
              <h3 className="text-sm font-semibold mb-2">Proxy URL:</h3>
              <p className="font-mono text-xs break-all bg-gray-100 p-2 rounded">{proxyUrl}</p>
            </div>
          )}
        </CardContent>
      </Card>
      
      {proxyUrl && (
        <Card>
          <CardHeader>
            <CardTitle>Image Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative bg-gray-100 rounded-lg p-4 min-h-[300px] flex items-center justify-center">
              {isLoading ? (
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
              ) : (
                <img 
                  src={proxyUrl} 
                  alt="Proxied image" 
                  className="max-w-full max-h-[500px] object-contain"
                  onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => {
                    console.error('Error loading image');
                    e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0yNCAxMmMwIDYuNjIzLTUuMzc3IDEyLTEyIDEycy0xMi01LjM3Ny0xMi0xMiA1LjM3Ny0xMiAxMi0xMiAxMiA1LjM3NyAxMiAxMnptLTEgMGMwLTYuMDcxLTQuOTI5LTExLTExLTExcy0xMSA0LjkyOS0xMSAxMSA0LjkyOSAxMSAxMSAxMSAxMS00LjkyOSAxMS0xMXptLTExLjUgNC44MjhjLjU1MiAwIDEgLjQ0OCAxIDFzLS40NDggMS0xIDEtMS0uNDQ4LTEtMS40NDgtMSAxLTEgMXptLjA1My03LjI0NmMtLjUzMSAwLS45OTQuMTk0LTEuMzg1LjU4MS0uMzkuMzg3LS41ODUuODYyLS41ODUgMS40MjQgMCAuNTUyLjQ0OCAxIC45OTkgMXMuOTk5LS40NDguOTk5LTFjMC0uMTYuMDU4LS4yOTQuMTczLS40MDguMTE2LS4xMTQuMjY4LS4xNy40NTQtLjE3LjE4NyAwIC4zNC4wNTYuNDU3LjE3LjExNi4xMTQuMTc0LjI0OC4xNzQuNDA4IDAgLjE1OS0uMDU4LjI5My0uMTc0LjQwNy0uMTE3LjExNC0uMjcuMTctLjQ1Ny4xNy0uNTUxIDAtLjk5OC40NDgtLjk5OCAxdjJjMCAuNTUyLjQ0OCAxIC45OTkgMXMuOTk5LS40NDguOTk5LTF2LTEuNTljLjY0LS4xMTUgMS4xOTItLjM5IDEuNjU2LS44MjUuNDY1LS40MzQuNjk3LS45NTYuNjk3LTEuNTY1IDAtLjYxLS4yMzItMS4xNTEtLjY5Ny0xLjYyNC0uNDY0LS40NzItMS4wMjYtLjcwOC0xLjY4Ni0uNzA4aC0uMDI2eiIvPjwvc3ZnPg==';
                    e.currentTarget.className = 'w-1/2 h-1/2 object-contain m-auto';
                    setStatus(prev => `${prev}\nError loading image`);
                  }}
                />
              )}
            </div>
          </CardContent>
        </Card>
      )}
      
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Test with OpenAI DALL-E URL</h2>
        <p className="mb-2">Copy a DALL-E URL from the test below and paste it above to test the proxy:</p>
        
        <div className="bg-gray-100 p-4 rounded-lg">
          <pre className="text-xs overflow-auto whitespace-pre-wrap">
            {`https://oaidalleapiprodscus.blob.core.windows.net/private/org-UnVoUSbSzKKBv2FRN0n61Ve6/user-NNTtbgAwVksYYlktxB8HvKmx/img-7EQnB3ZtVnmheoIMYONLDpyg.png?st=2025-05-07T15%3A40%3A13Z&se=2025-05-07T17%3A40%3A13Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=b1a0ae1f-618f-4548-84fd-8b16cacd5485&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-05-07T01%3A57%3A49Z&ske=2025-05-08T01%3A57%3A49Z&sks=b&skv=2024-08-04&sig=NItTRJSbi2u6ByYx3ttHTJG%2BROohgurLUSjU457g7HE%3D`}
          </pre>
        </div>
      </div>
    </div>
  );
}

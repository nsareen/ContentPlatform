"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ImageIcon, AlertTriangle, CheckCircle } from "lucide-react";

export default function TestImageProxyDirect() {
  const [imageUrl, setImageUrl] = useState("");
  const [proxyUrl, setProxyUrl] = useState("");
  const [directLoaded, setDirectLoaded] = useState(false);
  const [proxyLoaded, setProxyLoaded] = useState(false);
  const [directError, setDirectError] = useState(false);
  const [proxyError, setProxyError] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs((prev) => [...prev, `${new Date().toISOString().split("T")[1].split(".")[0]} - ${message}`]);
  };

  const testImage = () => {
    if (!imageUrl) {
      addLog("Please enter an image URL");
      return;
    }

    // Reset states
    setDirectLoaded(false);
    setProxyLoaded(false);
    setDirectError(false);
    setProxyError(false);
    
    // Set proxy URL
    const encodedUrl = encodeURIComponent(imageUrl);
    const timestamp = Date.now();
    const newProxyUrl = `http://localhost:8000/api/proxy/image?url=${encodedUrl}&t=${timestamp}`;
    setProxyUrl(newProxyUrl);
    
    addLog(`Testing direct URL: ${imageUrl}`);
    addLog(`Testing proxy URL: ${newProxyUrl}`);
  };

  // Sample public image URLs for testing
  const sampleUrls = [
    "https://images.unsplash.com/photo-1682687982501-1e58ab814714", // Unsplash image
    "https://picsum.photos/800/600", // Lorem Picsum
    "https://fastly.picsum.photos/id/237/500/500.jpg", // Specific Lorem Picsum
    "https://placehold.co/600x400/png", // Placeholder image
    "https://via.placeholder.com/300.png", // Another placeholder
  ];

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Image Proxy Direct Test</h1>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Test Image Loading</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Image URL</label>
              <div className="flex gap-2">
                <Input
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  placeholder="Enter image URL to test"
                  className="flex-1"
                />
                <Button onClick={testImage}>Test</Button>
              </div>
            </div>
            
            <div>
              <p className="text-sm text-gray-500 mb-2">Sample URLs (click to use):</p>
              <div className="space-y-2">
                {sampleUrls.map((url, index) => (
                  <div 
                    key={index}
                    className="text-xs p-2 bg-gray-100 rounded cursor-pointer hover:bg-gray-200 truncate"
                    onClick={() => setImageUrl(url)}
                  >
                    {url}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Direct Image
              {directLoaded && <CheckCircle className="h-4 w-4 text-green-500" />}
              {directError && <AlertTriangle className="h-4 w-4 text-red-500" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="aspect-square bg-gray-100 flex items-center justify-center rounded-md overflow-hidden">
              {imageUrl ? (
                <img
                  src={imageUrl}
                  alt="Direct image"
                  className="max-w-full max-h-full object-contain"
                  onLoad={() => {
                    setDirectLoaded(true);
                    addLog("Direct image loaded successfully");
                  }}
                  onError={() => {
                    setDirectError(true);
                    addLog("Error loading direct image");
                  }}
                />
              ) : (
                <div className="text-center">
                  <ImageIcon size={24} className="mx-auto mb-2 text-gray-400" />
                  <p className="text-sm text-gray-500">Enter a URL and click Test</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Proxied Image
              {proxyLoaded && <CheckCircle className="h-4 w-4 text-green-500" />}
              {proxyError && <AlertTriangle className="h-4 w-4 text-red-500" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="aspect-square bg-gray-100 flex items-center justify-center rounded-md overflow-hidden">
              {proxyUrl ? (
                <img
                  src={proxyUrl}
                  alt="Proxied image"
                  className="max-w-full max-h-full object-contain"
                  onLoad={() => {
                    setProxyLoaded(true);
                    addLog("Proxy image loaded successfully");
                  }}
                  onError={() => {
                    setProxyError(true);
                    addLog("Error loading proxy image");
                  }}
                  crossOrigin="anonymous"
                />
              ) : (
                <div className="text-center">
                  <ImageIcon size={24} className="mx-auto mb-2 text-gray-400" />
                  <p className="text-sm text-gray-500">Enter a URL and click Test</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-900 text-gray-100 p-4 rounded-md h-64 overflow-y-auto font-mono text-sm">
            {logs.length > 0 ? (
              logs.map((log, index) => (
                <div key={index} className="mb-1">
                  {log}
                </div>
              ))
            ) : (
              <div className="text-gray-500">No logs yet. Test an image to see logs.</div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

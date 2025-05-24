'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { BrandVoiceList } from '@/components/brand-voice/brand-voice-list';
import { brandVoiceService } from '@/lib/api/brand-voice-service';
// Import BrandVoice from the types directory instead of the component
import { BrandVoice } from '@/types/brand-voice';
import { AlertCircle } from 'lucide-react';
import { FloatingActions } from '@/components/brand-voice/floating-actions';

export default function BrandVoicesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [brandVoices, setBrandVoices] = useState<BrandVoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch brand voices with detailed logging and error handling
  const fetchBrandVoices = async () => {
    setIsLoading(true);
    setErrorMessage(null); // Clear any previous errors
    
    console.log('[BrandVoicesPage] Starting to fetch brand voices');
    
    try {
      // Make the API call through the service - now using the /api/voices/all/ endpoint directly
      console.log('[BrandVoicesPage] Calling brandVoiceService.getAllBrandVoices()');
      const voices = await brandVoiceService.getAllBrandVoices();
      
      console.log(`[BrandVoicesPage] Successfully fetched ${voices.length} brand voices:`, voices);
      setBrandVoices(voices);
      setErrorMessage(null);
    } catch (error) {
      console.error('[BrandVoicesPage] Error fetching brand voices:', error);
      
      // Log detailed error information
      if (error instanceof Error) {
        console.error('[BrandVoicesPage] Error message:', error.message);
        console.error('[BrandVoicesPage] Error stack:', error.stack);
        
        // Provide more specific error messages based on the error
        if (error.message.includes('Failed to fetch') || error.message === 'Load failed') {
          setErrorMessage('Failed to connect to the backend server. Please ensure the backend is running on port 8001.');
        } else if (error.message.includes('status 401') || error.message.includes('status 403')) {
          setErrorMessage('Authentication error. Please check your API token or login again.');
        } else if (error.message.includes('status 404')) {
          setErrorMessage('API endpoint not found. Please check the API configuration.');
        } else if (error.message.includes('status 500')) {
          setErrorMessage('Backend server error. Please check the server logs for details.');
        } else {
          setErrorMessage(`Failed to load brand voices: ${error.message}`);
        }
      } else {
        console.error('[BrandVoicesPage] Unknown error type:', typeof error);
        setErrorMessage('Failed to load brand voices: Unknown error. Check if the backend server is running.');
      }
    } finally {
      setIsLoading(false);
      console.log('[BrandVoicesPage] Fetch operation completed');
    }
  };
  
  // Fetch brand voices when component mounts
  useEffect(() => {
    console.log('Brand voices page mounted, fetching data');
    fetchBrandVoices();
  }, []);

  // Handle edit, delete, and publish actions
  const handleEdit = (voice: BrandVoice) => {
    window.location.href = `/brand-voices/${voice.id}/edit`;
  };

  const handleDelete = async (voice: BrandVoice) => {
    if (window.confirm(`Are you sure you want to delete ${voice.name}?`)) {
      try {
        setErrorMessage(null); // Clear any previous errors
        
        // Use the service to delete the brand voice - auth is handled internally
        await brandVoiceService.deleteBrandVoice(voice.id);
        
        // Refresh the data
        await fetchBrandVoices();
        alert(`${voice.name} has been deleted successfully`);
      } catch (error) {
        console.error('Failed to delete brand voice:', error);
        const errorMsg = error instanceof Error ? error.message : 'Unknown error occurred';
        setErrorMessage(`Failed to delete brand voice: ${errorMsg}`);
      }
    }
  };

  const handlePublish = async (voice: BrandVoice) => {
    try {
      setErrorMessage(null); // Clear any previous errors
      
      // Use the service to publish the brand voice - auth is handled internally
      await brandVoiceService.publishBrandVoice(voice.id);
      
      // Refresh the data
      await fetchBrandVoices();
      alert(`${voice.name} has been published successfully`);
    } catch (error) {
      console.error('Failed to publish brand voice:', error);
      const errorMsg = error instanceof Error ? error.message : 'Unknown error occurred';
      setErrorMessage(`Failed to publish brand voice: ${errorMsg}`);
    }
  };
  
  // Refresh button handler
  const handleRefresh = async () => {
    setErrorMessage(null); // Clear any previous errors
    try {
      await fetchBrandVoices();
    } catch (error) {
      console.error('Failed to refresh brand voices:', error);
      const errorMsg = error instanceof Error ? error.message : 'Unknown error occurred';
      setErrorMessage(`Failed to refresh brand voices: ${errorMsg}`);
    }
  };
  
  // Add error message display component with retry button
  const ErrorDisplay = () => {
    if (!errorMessage) return null;
    
    // Check if the error is a connection error
    const isConnectionError = 
      errorMessage.includes('unreachable') || 
      errorMessage.includes('connect to the server') || 
      errorMessage.includes('timed out');
    
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 mr-2 text-red-600" />
            <span>{errorMessage}</span>
          </div>
          {isConnectionError && (
            <button 
              onClick={() => fetchBrandVoices()} 
              className="px-3 py-1 bg-red-100 text-red-800 rounded-md text-sm hover:bg-red-200 transition-colors"
            >
              Retry
            </button>
          )}
        </div>
        {isConnectionError && (
          <div className="mt-2 text-sm text-red-700">
            <p>This could be due to:</p>
            <ul className="list-disc ml-5 mt-1">
              <li>The backend server is not running</li>
              <li>Your network connection is unstable</li>
              <li>CORS issues preventing the connection</li>
            </ul>
          </div>
        )}
      </div>
    );
  };
  
  // Filter brand voices based on search query and status filter
  const filteredVoices = brandVoices.filter((voice: BrandVoice) => {
    // Filter by search query
    const matchesSearch = voice.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      voice.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Filter by status
    const matchesStatus = statusFilter === 'all' || voice.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Add FloatingActions component for brand voice generator */}
      <FloatingActions />
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-[#1E2334]">Brand Voices</h2>
        <Link
          href="/brand-voices/new"
          className="px-4 py-2 bg-[#6D3BEB] text-white rounded-md text-sm font-medium hover:bg-[#5A26B8]"
        >
          Create Brand Voice
        </Link>
      </div>

      {/* Display error message if there is one */}
      <ErrorDisplay />

      <div className="bg-white p-6 rounded-lg border border-[#E2E8F0] shadow-sm">
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search brand voices..."
            className="w-full px-4 py-2 border border-[#E2E8F0] rounded-md focus:outline-none focus:ring-2 focus:ring-[#6D3BEB] focus:border-transparent"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex items-center space-x-4 mb-6">
          <button
            className={`px-3 py-1 ${statusFilter === 'all' ? 'bg-[#6D3BEB] text-white' : 'text-[#475569] hover:bg-[#F1F5F9]'} rounded-md text-sm`}
            onClick={() => setStatusFilter('all')}
          >
            All
          </button>
          <button
            className={`px-3 py-1 ${statusFilter === 'published' ? 'bg-[#6D3BEB] text-white' : 'text-[#475569] hover:bg-[#F1F5F9]'} rounded-md text-sm`}
            onClick={() => setStatusFilter('published')}
          >
            Published
          </button>
          <button
            className={`px-3 py-1 ${statusFilter === 'draft' ? 'bg-[#6D3BEB] text-white' : 'text-[#475569] hover:bg-[#F1F5F9]'} rounded-md text-sm`}
            onClick={() => setStatusFilter('draft')}
          >
            Draft
          </button>
          <button
            className={`px-3 py-1 ${statusFilter === 'under_review' ? 'bg-[#6D3BEB] text-white' : 'text-[#475569] hover:bg-[#F1F5F9]'} rounded-md text-sm`}
            onClick={() => setStatusFilter('under_review')}
          >
            Under Review
          </button>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#6D3BEB]"></div>
          </div>
        ) : brandVoices && brandVoices.length > 0 ? (
          <div className="space-y-4">
            {filteredVoices.map((voice: BrandVoice) => (
              <div key={voice.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer" onClick={() => window.location.href = `/brand-voices/${voice.id}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-[#1E2334] hover:text-[#6D3BEB]">
                      <Link href={`/brand-voices/${voice.id}`}>{voice.name}</Link>
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">{voice.description}</p>
                    <div className="mt-2 flex items-center space-x-2">
                      <span className={`px-2 py-0.5 text-xs rounded-full ${voice.status === 'published' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {voice.status.charAt(0).toUpperCase() + voice.status.slice(1)}
                      </span>
                      <span className="text-xs text-gray-500">Version {voice.version}</span>
                    </div>
                  </div>
                  <div className="flex space-x-2" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => window.location.href = `/brand-voices/${voice.id}`}
                      className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleEdit(voice)}
                      className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      Edit
                    </button>
                    {voice.status !== 'published' && (
                      <button
                        onClick={() => handlePublish(voice)}
                        className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                      >
                        Publish
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(voice)}
                      className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 border border-dashed border-gray-300 rounded-md">
            <p className="text-lg font-medium mb-2 text-gray-700">No brand voices found</p>
            <p className="text-gray-500 mb-4">
              {errorMessage ? 'An error occurred while loading brand voices.' : 'You haven\'t created any brand voices yet.'}
            </p>
            <Link
              href="/brand-voices/new"
              className="inline-block px-4 py-2 bg-[#6D3BEB] text-white rounded-md text-sm font-medium hover:bg-[#5A26B8]"
            >
              Create Your First Brand Voice
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

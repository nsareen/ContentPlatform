'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { brandVoiceService } from '@/lib/api/brand-voice-service';
import { BrandVoice } from '@/components/brand-voice/brand-voice-card';
import { FloatingActions } from '@/components/brand-voice/floating-actions';

export default function BrandVoiceDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;
  
  const [brandVoice, setBrandVoice] = useState<BrandVoice | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBrandVoice = async () => {
      try {
        const data = await brandVoiceService.getBrandVoice(id);
        setBrandVoice(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch brand voice:', err);
        setError('Failed to load brand voice. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBrandVoice();
  }, [id]);

  const handleDelete = async () => {
    if (!brandVoice) return;
    
    if (window.confirm(`Are you sure you want to delete ${brandVoice.name}?`)) {
      try {
        await brandVoiceService.deleteBrandVoice(id);
        router.push('/brand-voices');
      } catch (err) {
        console.error('Failed to delete brand voice:', err);
        alert('Failed to delete brand voice. Please try again.');
      }
    }
  };

  const handlePublish = async () => {
    if (!brandVoice) return;
    
    try {
      await brandVoiceService.publishBrandVoice(id);
      // Refresh the data
      const updatedVoice = await brandVoiceService.getBrandVoice(id);
      setBrandVoice(updatedVoice);
    } catch (err) {
      console.error('Failed to publish brand voice:', err);
      alert('Failed to publish brand voice. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Floating Actions */}
      {brandVoice && (
        <FloatingActions 
          brandVoiceId={id} 
          brandVoiceName={brandVoice.name} 
        />
      )}
      
      {/* Header */}
      <header className="bg-white border-b border-[#E2E8F0] px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-xl font-semibold text-[#1E2334]">
            Content Platform
          </Link>
          <nav className="flex items-center space-x-4">
            <Link href="/brand-voices" className="text-[#6D3BEB] font-medium">
              Brand Voices
            </Link>
            <Link href="/projects" className="text-[#475569] hover:text-[#1E2334]">
              Projects
            </Link>
            <Link href="/settings" className="text-[#475569] hover:text-[#1E2334]">
              Settings
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-6">
          <div className="flex items-center space-x-2">
            <Link href="/brand-voices" className="text-[#475569] hover:text-[#1E2334]">
              Brand Voices
            </Link>
            <span className="text-[#94A3B8]">/</span>
            <span className="text-[#1E2334]">
              {brandVoice?.name || 'Brand Voice Details'}
            </span>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#6D3BEB]"></div>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-500 mb-4">{error}</p>
              <button 
                className="px-4 py-2 bg-[#6D3BEB] text-white rounded-md text-sm font-medium hover:bg-[#5A26B8]"
                onClick={() => router.push('/brand-voices')}
              >
                Back to Brand Voices
              </button>
            </div>
          ) : brandVoice ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold text-[#1E2334]">{brandVoice.name}</h2>
                <div className="flex items-center space-x-3">
                  {brandVoice.status === 'draft' && (
                    <button
                      onClick={handlePublish}
                      className="px-4 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700"
                    >
                      Publish
                    </button>
                  )}
                  <Link
                    href={`/brand-voices/${id}/edit`}
                    className="px-4 py-2 bg-[#6D3BEB] text-white rounded-md text-sm font-medium hover:bg-[#5A26B8]"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={handleDelete}
                    className="px-4 py-2 bg-white border border-red-500 text-red-500 rounded-md text-sm font-medium hover:bg-red-50"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg border border-[#E2E8F0] shadow-sm">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 rounded-md bg-[#6D3BEB] flex items-center justify-center text-white text-xl font-semibold mr-4">
                    {brandVoice.name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="text-lg font-medium">{brandVoice.name}</h3>
                    <div className="flex items-center mt-1">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          brandVoice.status === "draft"
                            ? "bg-yellow-100 text-yellow-800"
                            : brandVoice.status === "published"
                            ? "bg-green-100 text-green-800"
                            : brandVoice.status === "under_review"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {brandVoice.status.charAt(0).toUpperCase() + brandVoice.status.slice(1)}
                      </span>
                      <span className="ml-2 text-sm text-[#475569]">Version {brandVoice.version}</span>
                    </div>
                  </div>
                </div>

                <div className="border-t border-[#E2E8F0] pt-4 mt-4">
                  <h4 className="text-sm font-medium text-[#475569] mb-2">Description</h4>
                  <p className="text-[#1E2334]">{brandVoice.description}</p>
                </div>

                {(brandVoice.voice_metadata?.personality || brandVoice.voice_metadata?.tonality) && (
                  <div className="border-t border-[#E2E8F0] pt-4 mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {brandVoice.voice_metadata.personality && (
                      <div>
                        <h4 className="text-sm font-medium text-[#475569] mb-2">Personality</h4>
                        <p className="text-[#1E2334]">{brandVoice.voice_metadata.personality}</p>
                      </div>
                    )}
                    {brandVoice.voice_metadata.tonality && (
                      <div>
                        <h4 className="text-sm font-medium text-[#475569] mb-2">Tonality</h4>
                        <p className="text-[#1E2334]">{brandVoice.voice_metadata.tonality}</p>
                      </div>
                    )}
                  </div>
                )}

                <div className="border-t border-[#E2E8F0] pt-4 mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-[#475569] mb-2">Do's</h4>
                    <div className="bg-[#F8FAFC] p-4 rounded-md border border-[#E2E8F0] whitespace-pre-line">
                      {brandVoice.dos || "No do's specified"}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-[#475569] mb-2">Don'ts</h4>
                    <div className="bg-[#F8FAFC] p-4 rounded-md border border-[#E2E8F0] whitespace-pre-line">
                      {brandVoice.donts || "No don'ts specified"}
                    </div>
                  </div>
                </div>

                <div className="border-t border-[#E2E8F0] pt-4 mt-4">
                  <h4 className="text-sm font-medium text-[#475569] mb-2">Timestamps</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <span className="text-xs text-[#94A3B8]">Created</span>
                      <p className="text-[#1E2334]">
                        {new Date(brandVoice.created_at).toLocaleString()}
                      </p>
                    </div>
                    {brandVoice.updated_at && (
                      <div>
                        <span className="text-xs text-[#94A3B8]">Last Updated</span>
                        <p className="text-[#1E2334]">
                          {new Date(brandVoice.updated_at).toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </main>
    </div>
  );
}

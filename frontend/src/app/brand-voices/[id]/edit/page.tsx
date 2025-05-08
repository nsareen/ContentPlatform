'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { BrandVoiceForm } from '@/components/brand-voice/brand-voice-form';
import { brandVoiceService } from '@/lib/api/brand-voice-service';
import { BrandVoice } from '@/components/brand-voice/brand-voice-card';
import { FloatingActions } from '@/components/brand-voice/floating-actions';

// Define the form data type to match our form
type BrandVoiceFormData = {
  name: string;
  description: string;
  dos?: string;
  donts?: string;
  voice_metadata?: {
    personality?: string;
    tonality?: string;
  };
};

export default function EditBrandVoicePage() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;
  
  const [brandVoice, setBrandVoice] = useState<BrandVoice | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
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

  const handleSubmit = async (data: BrandVoiceFormData) => {
    setIsSubmitting(true);
    try {
      await brandVoiceService.updateBrandVoice(id, data);
      router.push('/brand-voices');
    } catch (err) {
      console.error('Failed to update brand voice:', err);
      alert('Failed to update brand voice. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
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
            <span className="text-[#1E2334]">Edit Brand Voice</span>
          </div>

          <h2 className="text-2xl font-semibold text-[#1E2334]">
            Edit Brand Voice {brandVoice?.name ? `- ${brandVoice.name}` : ''}
          </h2>
          
          {/* Floating Actions for Playground Panel */}
          {brandVoice && (
            <FloatingActions 
              brandVoiceId={brandVoice.id} 
              brandVoiceName={brandVoice.name} 
            />
          )}
          
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
          ) : (
            <BrandVoiceForm 
              initialData={brandVoice || undefined}
              onSubmit={handleSubmit} 
              onCancel={() => router.push('/brand-voices')}
              isLoading={isSubmitting}
            />
          )}
        </div>
      </main>
    </div>
  );
}

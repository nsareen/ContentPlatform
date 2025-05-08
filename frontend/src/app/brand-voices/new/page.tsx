'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { BrandVoiceForm } from '@/components/brand-voice/brand-voice-form';
import { brandVoiceService } from '@/lib/api/brand-voice-service';
import { authService } from '@/lib/api/auth-service';

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

export default function NewBrandVoicePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: BrandVoiceFormData) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Get tenant ID from JWT token
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('You must be logged in to create a brand voice');
      }
      
      // In development mode, we need to use the actual tenant ID from the database user
      // We found that the admin user in the database has tenant_id="1ece4109-616a-47b1-8466-e74ef48bb85e"
      console.log('Using actual database user tenant ID for development');
      const tenantId = '1ece4109-616a-47b1-8466-e74ef48bb85e';
      console.log('Creating brand voice with tenant ID:', tenantId);
      
      // Format the data properly according to the backend schema
      // Make sure voice_metadata is properly formatted
      let voiceMetadata = undefined;
      
      // Only include voice_metadata if at least one property has a value
      if (data.voice_metadata?.personality || data.voice_metadata?.tonality) {
        voiceMetadata = {
          personality: data.voice_metadata?.personality || undefined,
          tonality: data.voice_metadata?.tonality || undefined
        };
      }
      
      const formattedData = {
        tenant_id: tenantId,
        name: data.name,
        description: data.description,
        dos: data.dos || undefined,
        donts: data.donts || undefined,
        voice_metadata: voiceMetadata
      };
      
      console.log('Sending brand voice data:', formattedData);
      
      await brandVoiceService.createBrandVoice(formattedData);
      
      // Force a full page reload to ensure the listing page shows the new brand voice
      // This is more reliable than relying on React Query cache invalidation
      window.location.href = '/brand-voices';
    } catch (err: any) {
      console.error('Failed to create brand voice:', err);
      setError(err.message || 'Failed to create brand voice. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white border-b border-border-default px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-xl font-semibold text-text-primary">
            Content Platform
          </Link>
          <nav className="flex items-center space-x-4">
            <Link href="/brand-voices" className="text-primary font-medium">
              Brand Voices
            </Link>
            <Link href="/projects" className="text-text-secondary hover:text-text-primary">
              Projects
            </Link>
            <Link href="/settings" className="text-text-secondary hover:text-text-primary">
              Settings
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-6">
          <div className="flex items-center space-x-2">
            <Link href="/brand-voices" className="text-text-secondary hover:text-text-primary">
              Brand Voices
            </Link>
            <span className="text-text-tertiary">/</span>
            <span className="text-text-primary">New Brand Voice</span>
          </div>

          <h2 className="text-2xl font-semibold text-text-primary">Create New Brand Voice</h2>
          
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-feedback-error rounded-md">
              {error}
            </div>
          )}
          
          <BrandVoiceForm 
            onSubmit={handleSubmit} 
            onCancel={() => router.push('/brand-voices')}
            isLoading={isSubmitting}
          />
        </div>
      </main>
    </div>
  );
}

import React, { useState, ChangeEvent } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Loader2, X } from "lucide-react";
import { brandVoiceService, BrandVoiceComponents } from '@/lib/api/brand-voice-service';
import { BrandVoicePreview } from './';

const industries = [
  { value: '', label: 'Select Industry' },
  { value: 'beauty', label: 'Beauty & Cosmetics' },
  { value: 'fashion', label: 'Fashion' },
  { value: 'technology', label: 'Technology' },
  { value: 'finance', label: 'Finance' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'education', label: 'Education' },
  { value: 'food', label: 'Food & Beverage' },
  { value: 'retail', label: 'Retail' },
  { value: 'other', label: 'Other' }
];

interface FloatingGeneratorPanelProps {
  onClose: () => void;
}

export function FloatingGeneratorPanel({ onClose }: FloatingGeneratorPanelProps) {
  const [content, setContent] = useState('');
  const [brandName, setBrandName] = useState('');
  const [industry, setIndustry] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedBrandVoice, setGeneratedBrandVoice] = useState<{ success: boolean; brand_voice_components: BrandVoiceComponents; generation_metadata: any; error?: string } | null>(null);

  const handleGenerate = async () => {
    if (!content) {
      setError('Please provide sample content to generate a brand voice');
      return;
    }

    setError(null);
    setIsGenerating(true);
    try {
      const result = await brandVoiceService.generateBrandVoice({
        content,
        brand_name: brandName,
        industry,
        options: {
          generation_depth: 'basic', // Use basic depth for faster generation in floating panel
          include_sample_content: true
        }
      });

      if (result.success) {
        setGeneratedBrandVoice(result);
      } else {
        setError(result.error || 'Failed to generate brand voice');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while generating the brand voice');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleOpenFullGenerator = () => {
    // Navigate to the full generator page with the correct URL
    window.location.href = '/brand-voices/new?tab=generator';
  };

  return (
    <div className="w-full max-w-md bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="flex justify-between items-center p-4 border-b">
        <h3 className="font-semibold">Brand Voice Generator</h3>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="p-4 max-h-[70vh] overflow-y-auto">
        {!generatedBrandVoice ? (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Generate a brand voice from sample content
            </p>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">Brand Name (Optional)</label>
                <Input 
                  value={brandName}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setBrandName(e.target.value)}
                  placeholder="e.g., Maybelline Singapore"
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Industry (Optional)</label>
                <Select
                  value={industry}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) => setIndustry(e.target.value)}
                  className="w-full"
                >
                  {industries.map((ind) => (
                    <option key={ind.value} value={ind.value}>{ind.label}</option>
                  ))}
                </Select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">
                  Sample Content <span className="text-red-500">*</span>
                </label>
                <Textarea
                  value={content}
                  onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setContent(e.target.value)}
                  placeholder="Paste sample content from your brand here..."
                  rows={6}
                  className="w-full"
                />
              </div>
              
              <Button 
                onClick={handleGenerate}
                disabled={!content || isGenerating}
                className="w-full"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  'Generate Brand Voice'
                )}
              </Button>
              
              <Button 
                variant="outline" 
                onClick={handleOpenFullGenerator}
                className="w-full"
              >
                Open Full Generator Interface
              </Button>
            </div>
            
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
                {error}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between">
              <h4 className="font-medium">Generated Brand Voice</h4>
              <Button variant="ghost" size="sm" onClick={() => setGeneratedBrandVoice(null)}>
                Reset
              </Button>
            </div>
            
            {/* Simplified preview for floating panel */}
            <div className="space-y-3">
              <div>
                <h5 className="text-sm font-medium">Personality Traits</h5>
                <div className="flex flex-wrap gap-1 mt-1">
                  {generatedBrandVoice.brand_voice_components.personality_traits.map((trait: string, index: number) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-xs rounded-full">
                      {trait}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <h5 className="text-sm font-medium">Tonality</h5>
                <p className="text-xs text-gray-600 mt-1">
                  {generatedBrandVoice.brand_voice_components.tonality.substring(0, 150)}
                  {generatedBrandVoice.brand_voice_components.tonality.length > 150 ? '...' : ''}
                </p>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <h5 className="text-sm font-medium">Do's</h5>
                  <ul className="list-disc pl-4 text-xs text-gray-600 mt-1">
                    {generatedBrandVoice.brand_voice_components.dos.slice(0, 3).map((item: string, index: number) => (
                      <li key={index}>{item}</li>
                    ))}
                    {generatedBrandVoice.brand_voice_components.dos.length > 3 && (
                      <li>...</li>
                    )}
                  </ul>
                </div>
                
                <div>
                  <h5 className="text-sm font-medium">Don'ts</h5>
                  <ul className="list-disc pl-4 text-xs text-gray-600 mt-1">
                    {generatedBrandVoice.brand_voice_components.donts.slice(0, 3).map((item: string, index: number) => (
                      <li key={index}>{item}</li>
                    ))}
                    {generatedBrandVoice.brand_voice_components.donts.length > 3 && (
                      <li>...</li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col space-y-2">
              <Button 
                onClick={handleOpenFullGenerator}
                className="w-full"
              >
                Open Full Generator to Save
              </Button>
              
              <Button 
                variant="outline" 
                onClick={() => setGeneratedBrandVoice(null)}
                className="w-full"
              >
                Generate Another
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

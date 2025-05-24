import React, { useState, ChangeEvent } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Loader2 } from "lucide-react";
import { brandVoiceService, BrandVoiceComponents } from '@/lib/api/brand-voice-service';
import { BrandVoicePreview } from './generator-components';

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
  { value: 'travel', label: 'Travel & Hospitality' },
  { value: 'entertainment', label: 'Entertainment & Media' },
  { value: 'other', label: 'Other' }
];

export default function GeneratorPanel() {
  const [content, setContent] = useState('');
  const [brandName, setBrandName] = useState('');
  const [industry, setIndustry] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedBrandVoice, setGeneratedBrandVoice] = useState<{ success: boolean; brand_voice_components: BrandVoiceComponents; generation_metadata: any; error?: string } | null>(null);
  const [saveName, setSaveName] = useState('');
  const [saveDescription, setSaveDescription] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

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
        target_audience: targetAudience,
        options: {
          generation_depth: 'standard',
          include_sample_content: true
        }
      });

      if (result.success) {
        setGeneratedBrandVoice(result);
        setSaveName(brandName || 'New Brand Voice');
        setSaveDescription(`Brand voice generated from ${industry || 'content'} sample.`);
      } else {
        setError(result.error || 'Failed to generate brand voice');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while generating the brand voice');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!generatedBrandVoice || !saveName) {
      setError('Please provide a name for the brand voice');
      return;
    }

    setError(null);
    setIsSaving(true);
    try {
      const result = await brandVoiceService.saveBrandVoice({
        brand_voice_components: generatedBrandVoice.brand_voice_components,
        generation_metadata: generatedBrandVoice.generation_metadata,
        source_content: content,
        name: saveName,
        description: saveDescription
      });

      if (result.success) {
        setSaveSuccess(true);
      } else {
        setError(result.error || 'Failed to save brand voice');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while saving the brand voice');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    setGeneratedBrandVoice(null);
    setSaveSuccess(false);
  };

  return (
    <div className="flex flex-col space-y-6 p-4 max-w-4xl mx-auto">
      <div className="flex flex-col space-y-2">
        <h2 className="text-2xl font-bold">AI Brand Voice Generator</h2>
        <p className="text-gray-600">
          Paste sample content from your brand, and we'll automatically generate a brand voice profile.
        </p>
      </div>

      {!generatedBrandVoice && !saveSuccess && (
        <Card className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
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
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Target Audience (Optional)</label>
            <Input 
              value={targetAudience}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setTargetAudience(e.target.value)}
              placeholder="e.g., Women 18-35 interested in beauty products"
              className="w-full"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">
              Sample Content <span className="text-red-500">*</span>
            </label>
            <Textarea
              value={content}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setContent(e.target.value)}
              placeholder="Paste sample content from your brand here (product descriptions, marketing copy, etc.)"
              rows={8}
              className="w-full"
            />
            <p className="text-sm text-gray-500 mt-1">
              The more representative content you provide, the better the generated brand voice will be.
            </p>
          </div>
          
          <Button 
            onClick={handleGenerate}
            disabled={!content || isGenerating}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Brand Voice...
              </>
            ) : (
              'Generate Brand Voice'
            )}
          </Button>
          
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
              {error}
            </div>
          )}
        </Card>
      )}

      {generatedBrandVoice && !saveSuccess && (
        <div className="space-y-6">
          <BrandVoicePreview 
            brandVoice={generatedBrandVoice.brand_voice_components}
            onEdit={() => {/* Edit logic */}}
          />
          
          <Card className="p-6">
            <h3 className="text-lg font-bold mb-4">Save Brand Voice</h3>
            
            <div className="grid grid-cols-1 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Brand Voice Name <span className="text-red-500">*</span>
                </label>
                <Input 
                  value={saveName}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setSaveName(e.target.value)}
                  placeholder="Enter a name for this brand voice"
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Description (Optional)</label>
                <Textarea
                  value={saveDescription}
                  onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setSaveDescription(e.target.value)}
                  placeholder="Add a description for this brand voice"
                  rows={3}
                  className="w-full"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={handleReset}>
                Start Over
              </Button>
              <Button 
                onClick={handleSave}
                disabled={!saveName || isSaving}
              >
                {isSaving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Brand Voice'
                )}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {saveSuccess && (
        <Card className="p-6 text-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <h3 className="text-xl font-bold text-green-700">Brand Voice Saved Successfully!</h3>
            
            <p className="text-gray-600 max-w-md">
              Your brand voice has been created and is now available in your brand voice library.
            </p>
            
            <div className="flex space-x-3 pt-4">
              <Button variant="outline" onClick={handleReset}>
                Create Another Brand Voice
              </Button>
              <Button onClick={() => window.location.href = '/brand-voices'}>
                Go to Brand Voices
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

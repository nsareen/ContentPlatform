'use client';

import React, { useState, ChangeEvent, FormEvent } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Loader2 } from "lucide-react";
import { brandVoiceService, BrandVoiceComponents } from '@/lib/api/brand-voice-service';
import { BrandVoicePreview } from './brand-voice-preview';

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

interface GeneratorPanelProps {
  onSave: (brandVoice: any) => void;
  onCancel: () => void;
}

export function GeneratorPanel({ onSave, onCancel }: GeneratorPanelProps) {
  const [content, setContent] = useState('');
  const [brandName, setBrandName] = useState('');
  const [description, setDescription] = useState('');
  const [industry, setIndustry] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedBrandVoice, setGeneratedBrandVoice] = useState<{ 
    success: boolean; 
    brand_voice_components: BrandVoiceComponents; 
    generation_metadata: any; 
    error?: string 
  } | null>(null);

  const handleGenerate = async (e: FormEvent) => {
    e.preventDefault();
    
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
          generation_depth: 'detailed', // Use detailed depth for full generator
          include_sample_content: true
        }
      });

      if (result.success) {
        setGeneratedBrandVoice(result);
        // Set the description if it's not already set
        if (!description && brandName) {
          setDescription(`Brand voice for ${brandName}`);
        }
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
    if (!generatedBrandVoice) {
      setError('Please generate a brand voice first');
      return;
    }

    if (!brandName) {
      setError('Please provide a name for your brand voice');
      return;
    }

    setError(null);
    setIsSaving(true);
    try {
      const saveData = {
        name: brandName,
        description: description || `Brand voice for ${brandName}`,
        brand_voice_components: generatedBrandVoice.brand_voice_components,
        generation_metadata: generatedBrandVoice.generation_metadata,
        source_content: content
      };

      const result = await brandVoiceService.saveBrandVoice(saveData);
      
      if (result.success) {
        onSave(result.brand_voice);
      } else {
        setError(result.error || 'Failed to save brand voice');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while saving the brand voice');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <h3 className="text-lg font-medium mb-4">Generate Brand Voice from Content</h3>
        
        {!generatedBrandVoice ? (
          <form onSubmit={handleGenerate} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Brand Name</label>
                <Input 
                  value={brandName}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setBrandName(e.target.value)}
                  placeholder="e.g., Acme Corporation"
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
            
            <div>
              <label className="block text-sm font-medium mb-1">
                Sample Content <span className="text-red-500">*</span>
              </label>
              <p className="text-sm text-gray-500 mb-2">
                Paste content that represents your brand's voice. The AI will analyze this to generate a brand voice profile.
              </p>
              <Textarea 
                value={content}
                onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setContent(e.target.value)}
                placeholder="Paste your sample content here (e.g., website copy, marketing materials, etc.)"
                className="w-full min-h-[200px]"
                required
              />
            </div>
            
            <div className="flex space-x-3">
              <Button 
                type="submit"
                disabled={!content || isGenerating}
                className="w-full md:w-auto"
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
                type="button"
                variant="outline" 
                onClick={onCancel}
                className="w-full md:w-auto"
              >
                Cancel
              </Button>
            </div>
            
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
                {error}
              </div>
            )}
          </form>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Brand Name</label>
                <Input 
                  value={brandName}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setBrandName(e.target.value)}
                  placeholder="e.g., Acme Corporation"
                  className="w-full"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <Input 
                  value={description}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setDescription(e.target.value)}
                  placeholder="Brief description of your brand voice"
                  className="w-full"
                />
              </div>
            </div>
            
            <BrandVoicePreview 
              brandVoice={generatedBrandVoice.brand_voice_components}
            />
            
            <div className="flex space-x-3">
              <Button 
                onClick={handleSave}
                disabled={!brandName || isSaving}
                className="w-full md:w-auto"
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
              
              <Button 
                variant="outline" 
                onClick={() => setGeneratedBrandVoice(null)}
                className="w-full md:w-auto"
              >
                Regenerate
              </Button>
              
              <Button 
                variant="outline" 
                onClick={onCancel}
                className="w-full md:w-auto"
              >
                Cancel
              </Button>
            </div>
            
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
                {error}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

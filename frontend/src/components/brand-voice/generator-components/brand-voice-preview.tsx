import React from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Edit } from "lucide-react";

interface BrandVoicePreviewProps {
  brandVoice: {
    personality_traits: string[];
    tonality: string;
    identity: string;
    dos: string[];
    donts: string[];
    sample_content: string;
  };
  onEdit?: (section: string) => void;
}

export function BrandVoicePreview({ brandVoice, onEdit }: BrandVoicePreviewProps) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h3 className="text-xl font-bold">Generated Brand Voice Profile</h3>
        <p className="text-gray-600">
          AI has analyzed your sample content and generated the following brand voice profile.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-4 overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-medium">Personality Traits</h4>
            {onEdit && (
              <Button size="sm" variant="ghost" onClick={() => onEdit('personality_traits')}>
                <Edit size={16} className="mr-1" /> Edit
              </Button>
            )}
          </div>
          <div className="flex flex-wrap gap-2 mb-4">
            {brandVoice.personality_traits.map((trait, index) => (
              <Badge key={index} variant="outline" className="capitalize">{trait}</Badge>
            ))}
          </div>
          <div className="mt-4">
            <h4 className="font-medium mb-2">Tonality</h4>
            <p className="text-sm text-gray-600 whitespace-pre-line">{brandVoice.tonality}</p>
          </div>
        </Card>
        
        <Card className="p-4 overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-medium">Brand Identity</h4>
            {onEdit && (
              <Button size="sm" variant="ghost" onClick={() => onEdit('identity')}>
                <Edit size={16} className="mr-1" /> Edit
              </Button>
            )}
          </div>
          <p className="text-sm text-gray-600 whitespace-pre-line">{brandVoice.identity}</p>
        </Card>
        
        <Card className="p-4 overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-medium">Do's</h4>
            {onEdit && (
              <Button size="sm" variant="ghost" onClick={() => onEdit('dos')}>
                <Edit size={16} className="mr-1" /> Edit
              </Button>
            )}
          </div>
          <ul className="list-disc pl-5 text-sm text-gray-600 space-y-2">
            {brandVoice.dos.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </Card>
        
        <Card className="p-4 overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-medium">Don'ts</h4>
            {onEdit && (
              <Button size="sm" variant="ghost" onClick={() => onEdit('donts')}>
                <Edit size={16} className="mr-1" /> Edit
              </Button>
            )}
          </div>
          <ul className="list-disc pl-5 text-sm text-gray-600 space-y-2">
            {brandVoice.donts.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </Card>
      </div>
      
      <Card className="p-4 overflow-hidden">
        <div className="flex justify-between items-start mb-2">
          <h4 className="font-medium">Sample Content</h4>
          {onEdit && (
            <Button size="sm" variant="ghost" onClick={() => onEdit('sample_content')}>
              <Edit size={16} className="mr-1" /> Edit
            </Button>
          )}
        </div>
        <div className="bg-gray-50 p-3 rounded text-sm whitespace-pre-line">
          {brandVoice.sample_content}
        </div>
      </Card>
    </div>
  );
}

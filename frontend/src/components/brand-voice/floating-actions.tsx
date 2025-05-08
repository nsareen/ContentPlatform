"use client";

import React, { useState } from 'react';
import { MessageSquare, Lightbulb, Wand2, BarChart, HelpCircle, ImageIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { PlaygroundPanel } from './playground-panel';
import RichPlaygroundPanel from './rich-playground-panel-v2';

interface FloatingActionsProps {
  brandVoiceId?: string;
  brandVoiceName?: string;
}

export function FloatingActions({ brandVoiceId, brandVoiceName }: FloatingActionsProps) {
  const [activePanel, setActivePanel] = useState<string | null>(null);
  
  const togglePanel = (panelName: string) => {
    setActivePanel(activePanel === panelName ? null : panelName);
  };
  
  const closePanel = () => {
    setActivePanel(null);
  };

  return (
    <>
      <div className="fixed right-4 top-1/2 transform -translate-y-1/2 flex flex-col space-y-2 z-40">
        <ActionButton 
          icon={MessageSquare} 
          label="Text Playground" 
          isActive={activePanel === 'playground'}
          onClick={() => togglePanel('playground')}
        />
        <ActionButton 
          icon={ImageIcon} 
          label="Rich Media" 
          isActive={activePanel === 'rich-playground'}
          onClick={() => togglePanel('rich-playground')}
        />
        <ActionButton 
          icon={Lightbulb} 
          label="Ideas" 
          isActive={activePanel === 'ideas'}
          onClick={() => togglePanel('ideas')}
        />
        <ActionButton 
          icon={Wand2} 
          label="Refine" 
          isActive={activePanel === 'refine'}
          onClick={() => togglePanel('refine')}
        />
        <ActionButton 
          icon={BarChart} 
          label="Analytics" 
          isActive={activePanel === 'analytics'}
          onClick={() => togglePanel('analytics')}
        />
        <ActionButton 
          icon={HelpCircle} 
          label="Help" 
          isActive={activePanel === 'help'}
          onClick={() => togglePanel('help')}
        />
      </div>
      
      {/* Panels */}
      <PlaygroundPanel 
        isOpen={activePanel === 'playground'} 
        onClose={closePanel}
        brandVoiceId={brandVoiceId}
        brandVoiceName={brandVoiceName}
      />
      
      <RichPlaygroundPanel 
        isOpen={activePanel === 'rich-playground'} 
        onClose={closePanel}
        brandVoiceId={brandVoiceId}
        brandVoiceName={brandVoiceName}
      />
      
      {/* Other panels would be implemented similarly */}
    </>
  );
}

interface ActionButtonProps {
  icon: React.ElementType;
  label: string;
  isActive: boolean;
  onClick: () => void;
}

function ActionButton({ icon: Icon, label, isActive, onClick }: ActionButtonProps) {
  return (
    <div className="relative group">
      <button
        onClick={onClick}
        className={cn(
          "w-10 h-10 rounded-full flex items-center justify-center shadow-md transition-colors",
          isActive 
            ? "bg-primary text-white" 
            : "bg-white text-gray-700 hover:bg-gray-100"
        )}
        aria-label={label}
      >
        <Icon size={20} />
      </button>
      
      {/* Tooltip */}
      <div className="absolute right-full mr-2 top-1/2 transform -translate-y-1/2 hidden group-hover:block">
        <div className="bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
          {label}
        </div>
      </div>
    </div>
  );
}

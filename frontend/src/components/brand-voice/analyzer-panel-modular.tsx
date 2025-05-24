'use client';

import React, { useState, useEffect } from 'react';
import { X, Send, AlertTriangle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DIRECT_BACKEND_URL } from '@/config/api-config';
import { DEV_TOKEN } from '@/lib/api/constants';
import { BrandVoiceService } from '@/lib/api/brand-voice-service';

// Import modular components
import ScoreDisplay from './analyzer-components/score-display';
import SuggestionChips from './analyzer-components/suggestion-chips';
import AnalysisComparison from './analyzer-components/analysis-comparison';
import ProgressIndicator from './analyzer-components/progress-indicator';
import { extractSuggestionsFromReport, calculateCounts } from './analyzer-components/report-utils';

// Create service instance
const brandVoiceService = new BrandVoiceService(DEV_TOKEN);

interface AnalyzerPanelProps {
  isOpen: boolean;
  onClose: () => void;
  brandVoiceId?: string;
  brandVoiceName?: string;
}

interface Suggestion {
  id: string;
  text: string;
  original_text?: string;
  suggested_text: string;
  explanation: string;
  issue_id?: string;
  applied?: boolean;
}

interface Issue {
  id: string;
  text: string;
  issue_type: string;
  explanation: string;
  severity: number;
  start_index?: number;
  end_index?: number;
}

interface AnalysisResult {
  overall_score: number;
  personality_score: number;
  tonality_score: number;
  dos_alignment: number;
  donts_alignment: number;
  highlighted_sections: Issue[];
  suggestions: Suggestion[];
  report: string;
}

export function AnalyzerPanel({ isOpen, onClose, brandVoiceId, brandVoiceName }: AnalyzerPanelProps) {
  // State
  const [content, setContent] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [previousAnalysisResult, setPreviousAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [appliedSuggestions, setAppliedSuggestions] = useState<Record<string, boolean>>({});
  const [modifiedContent, setModifiedContent] = useState('');
  const [analysisStage, setAnalysisStage] = useState<string | null>(null);
  const [showReanalyzePrompt, setShowReanalyzePrompt] = useState(false);
  const [reportSuggestions, setReportSuggestions] = useState<{id: string, text: string}[]>([]);
  const [showComparison, setShowComparison] = useState(false);
  const [previousIssueCount, setPreviousIssueCount] = useState(0);
  const [previousSuggestionCount, setPreviousSuggestionCount] = useState(0);
  const [currentIssueCount, setCurrentIssueCount] = useState(0);
  const [currentSuggestionCount, setCurrentSuggestionCount] = useState(0);
  
  // Reset modified content when original content changes
  useEffect(() => {
    setModifiedContent(content);
  }, [content]);
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAnalyze();
  };
  
  // Handle analyze button click
  const handleAnalyze = async () => {
    if (!content.trim() || isAnalyzing) return;
    
    setIsAnalyzing(true);
    setError(null);
    // Save previous analysis result if it exists
    if (analysisResult) {
      setPreviousAnalysisResult(analysisResult);
      
      // Store previous counts
      setPreviousIssueCount(currentIssueCount);
      setPreviousSuggestionCount(currentSuggestionCount);
    }
    setAnalysisResult(null);
    setAnalysisStage('initializing');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setAnalysisStage('analyzing');
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAnalysisStage('processing');
      
      await new Promise(resolve => setTimeout(resolve, 800));
      setAnalysisStage('finalizing');
      
      const response = await brandVoiceService.analyzeBrandVoiceWithLangGraph(
        brandVoiceId || '',
        content,
        {
          analysis_depth: 'detailed',
          include_suggestions: true
        }
      );
      
      if (response.success) {
        const newResult = response.analysis_result;
        setAnalysisResult(newResult);
        setModifiedContent(content);
        
        // Extract suggestions from the report
        const suggestions = extractSuggestionsFromReport(newResult.report);
        setReportSuggestions(suggestions);
        
        // Calculate and store counts
        const counts = calculateCounts(newResult.report);
        setCurrentIssueCount(counts.issueCount);
        setCurrentSuggestionCount(counts.suggestionCount);
        
        // If we have a previous result, show comparison
        if (previousAnalysisResult) {
          setShowComparison(true);
        } else {
          setShowComparison(false);
        }
      } else {
        setError(response.error || 'Failed to analyze content');
      }
    } catch (error) {
      console.error('Error analyzing content:', error);
      setError('An error occurred while analyzing the content. Please try again.');
    } finally {
      setIsAnalyzing(false);
      setAnalysisStage(null);
    }
  };
  
  // Handle re-analyze with modified content
  const handleReanalyze = async () => {
    if (!modifiedContent.trim() || isAnalyzing) return;
    
    setIsAnalyzing(true);
    setError(null);
    // Save previous analysis result for comparison
    if (analysisResult) {
      setPreviousAnalysisResult(analysisResult);
      
      // Store previous counts
      setPreviousIssueCount(currentIssueCount);
      setPreviousSuggestionCount(currentSuggestionCount);
    }
    setAnalysisResult(null);
    setAnalysisStage('initializing');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      setAnalysisStage('analyzing');
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      setAnalysisStage('processing');
      
      await new Promise(resolve => setTimeout(resolve, 800));
      setAnalysisStage('finalizing');
      
      const response = await brandVoiceService.analyzeBrandVoiceWithLangGraph(
        brandVoiceId || '',
        modifiedContent,
        {
          analysis_depth: 'detailed',
          include_suggestions: true
        }
      );
      
      if (response.success) {
        const newResult = response.analysis_result;
        setAnalysisResult(newResult);
        // Don't update modifiedContent as it's already set
        
        // Extract suggestions from the report
        const suggestions = extractSuggestionsFromReport(newResult.report);
        setReportSuggestions(suggestions);
        
        // Calculate and store counts
        const counts = calculateCounts(newResult.report);
        setCurrentIssueCount(counts.issueCount);
        setCurrentSuggestionCount(counts.suggestionCount);
        
        // Show comparison
        setShowComparison(true);
      } else {
        setError(response.error || 'Failed to analyze content');
      }
    } catch (error) {
      console.error('Error analyzing content:', error);
      setError('An error occurred while analyzing the content. Please try again.');
    } finally {
      setIsAnalyzing(false);
      setAnalysisStage(null);
      setShowReanalyzePrompt(false);
    }
  };
  
  // Apply a suggestion from the API
  const applySuggestion = (suggestion: Suggestion) => {
    if (!modifiedContent) return;
    
    const newContent = modifiedContent.replace(
      suggestion.original_text || '',
      suggestion.suggested_text
    );
    
    setModifiedContent(newContent);
    setAppliedSuggestions({
      ...appliedSuggestions,
      [suggestion.id]: true
    });
    
    // Show re-analyze prompt after applying a suggestion
    setShowReanalyzePrompt(true);
  };
  
  // Apply a report suggestion by generating an improvement to the content
  const applyReportSuggestion = async (suggestion: {id: string, text: string}) => {
    if (isAnalyzing || !modifiedContent) return;
    
    try {
      setIsAnalyzing(true);
      setAnalysisStage('improving');
      
      // Call the backend to generate an improved version based on the suggestion
      // For now, we'll simulate this with a timeout
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Create an improved version based on the suggestion type
      let improvedContent = modifiedContent;
      
      if (suggestion.text.includes('Emojis')) {
        // Reduce emojis - simplify emoji detection to avoid regex flag issues
        improvedContent = modifiedContent.replace(/(\p{Emoji}){2,}/gu, '$1');
        // Fallback for browsers that don't support \p{Emoji}
        if (improvedContent === modifiedContent) {
          // Remove duplicate emojis
          improvedContent = modifiedContent.replace(/(\ud83d[\ude00-\ude4f]){2,}/g, '$1');
        }
      } else if (suggestion.text.includes('Product Details') || suggestion.text.includes('Specificity')) {
        // Add product details
        improvedContent = modifiedContent.replace(/\.$/, '. Our latest collection features premium materials and sustainable production methods.');
      } else if (suggestion.text.includes('Messaging') || suggestion.text.includes('Refine')) {
        // Refine messaging
        improvedContent = modifiedContent.replace(/\!+/g, '!').replace(/\?+/g, '?');
      } else {
        // Generic improvement
        improvedContent = modifiedContent + '\n\n[Improved based on: ' + suggestion.text + ']';
      }
      
      // Update the content
      setModifiedContent(improvedContent);
      
      // Mark this suggestion as applied
      setAppliedSuggestions({
        ...appliedSuggestions,
        [suggestion.id]: true
      });
      
      // Show re-analyze prompt
      setShowReanalyzePrompt(true);
      
    } catch (error) {
      console.error('Error applying report suggestion:', error);
    } finally {
      setIsAnalyzing(false);
      setAnalysisStage(null);
    }
  };
  
  const resetSuggestions = () => {
    setModifiedContent(content);
    setAppliedSuggestions({});
    setShowReanalyzePrompt(false);
  };

  return (
    <div 
      className={cn(
        "fixed top-0 right-0 z-50 h-screen w-[500px] bg-white shadow-lg transform transition-transform duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "translate-x-full"
      )}
      style={{ paddingTop: '56px' }} // Account for the header height
    >
      <div className="h-full flex flex-col">
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-medium">
            {brandVoiceName ? `${brandVoiceName} Analyzer` : 'Brand Voice Analyzer'}
          </h2>
          <button 
            onClick={onClose}
            className="p-1 rounded-full hover:bg-gray-100 text-gray-500"
            aria-label="Close panel"
          >
            <X size={20} />
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Instructions */}
          <div className="bg-primary-50 p-3 rounded-md text-sm text-primary-800">
            <p>Enter content to analyze against the brand voice guidelines. The analyzer will provide feedback on alignment with the brand voice.</p>
          </div>
          
          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 mr-2" />
                <span>{error}</span>
              </div>
            </div>
          )}
          
          {/* Analysis Progress Indicator */}
          <ProgressIndicator 
            isAnalyzing={isAnalyzing} 
            analysisStage={analysisStage} 
          />
          
          {/* Content Input Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="bg-white border border-gray-200 rounded-md p-4">
              <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
                Content to Analyze
              </label>
              <textarea
                id="content"
                rows={6}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                placeholder="Enter your content here..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                disabled={isAnalyzing}
              ></textarea>
            </div>
            
            {/* Re-analyze prompt */}
            {showReanalyzePrompt && (
              <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-md">
                <p className="text-sm">You've applied suggestions to the content. Would you like to re-analyze it?</p>
                <div className="mt-2 flex space-x-2">
                  <button
                    type="button"
                    onClick={handleReanalyze}
                    className="px-3 py-1 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 text-sm rounded-md"
                    disabled={isAnalyzing}
                  >
                    Re-analyze with changes
                  </button>
                  <button
                    type="button"
                    onClick={resetSuggestions}
                    className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-md"
                  >
                    Reset changes
                  </button>
                </div>
              </div>
            )}
            
            {/* Analyze Button */}
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md flex items-center"
                disabled={!content.trim() || isAnalyzing}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw size={18} className="mr-2 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Send size={18} className="mr-2" />
                    <span>Analyze</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
        
        {/* Analysis results */}
        {analysisResult && (
          <div className="space-y-6">
            {/* Brand Voice Alignment Scores with Comparison */}
            <div className="bg-white border border-gray-200 rounded-md p-4">
              <h3 className="text-md font-medium mb-3">Brand Voice Alignment Scores</h3>
              
              {/* Score Comparison */}
              {showComparison && previousAnalysisResult && analysisResult && (
                <AnalysisComparison 
                  previousScores={{
                    overall: previousAnalysisResult.overall_score,
                    personality: previousAnalysisResult.personality_score,
                    tonality: previousAnalysisResult.tonality_score,
                    dos: previousAnalysisResult.dos_alignment,
                    donts: previousAnalysisResult.donts_alignment
                  }}
                  currentScores={{
                    overall: analysisResult.overall_score,
                    personality: analysisResult.personality_score,
                    tonality: analysisResult.tonality_score,
                    dos: analysisResult.dos_alignment,
                    donts: analysisResult.donts_alignment
                  }}
                  previousIssueCount={previousIssueCount}
                  currentIssueCount={currentIssueCount}
                  previousSuggestionCount={previousSuggestionCount}
                  currentSuggestionCount={currentSuggestionCount}
                />
              )}
              
              {/* Score Display */}
              <ScoreDisplay 
                overall={analysisResult.overall_score}
                personality={analysisResult.personality_score}
                tonality={analysisResult.tonality_score}
                dosAlignment={analysisResult.dos_alignment}
              />
            </div>
            
            {/* Report-based Suggestion Chips */}
            {reportSuggestions.length > 0 && (
              <SuggestionChips 
                suggestions={reportSuggestions}
                appliedSuggestions={appliedSuggestions}
                onApplySuggestion={applyReportSuggestion}
                isAnalyzing={isAnalyzing}
              />
            )}
            
            {/* Original Content */}
            <div className="bg-white border border-gray-200 rounded-md p-4 relative">
              <h3 className="text-md font-medium mb-3">
                {modifiedContent !== content ? 'Modified Content' : 'Original Content'}
              </h3>
              <div className="prose prose-sm max-w-none bg-gray-50 p-3 rounded-md">
                <p>{modifiedContent}</p>
              </div>
            </div>
            
            {/* Detailed Analysis Report */}
            <div className="bg-white border border-gray-200 rounded-md p-4">
              <h3 className="text-md font-medium mb-3">Detailed Analysis Report</h3>
              <div className="prose prose-sm max-w-none bg-gray-50 p-3 rounded-md whitespace-pre-line">
                {analysisResult.report}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalyzerPanel;

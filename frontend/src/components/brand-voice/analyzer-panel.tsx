'use client';

import React, { useState, useEffect } from 'react';
import { X, Send, AlertTriangle, RefreshCw, Loader2, Copy, Check, ThumbsUp, ThumbsDown, Wand2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DEV_TOKEN } from '@/lib/api/constants';
import brandVoiceService from '@/lib/api/brand-voice-service';

interface AnalyzerPanelProps {
  isOpen: boolean;
  onClose: () => void;
  brandVoiceId?: string;
  brandVoiceName?: string;
}

interface Suggestion {
  id: string;
  original_text: string;
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
}

interface AnalysisResult {
  overall_score: number;
  personality_score: number;
  tonality_score: number;
  dos_alignment: number;
  donts_alignment: number;
  report: string;
  issues?: Issue[];
  suggestions?: Suggestion[];
}

const AnalyzerPanel: React.FC<AnalyzerPanelProps> = ({
  isOpen,
  onClose,
  brandVoiceId,
  brandVoiceName
}) => {
  // State for content and analysis
  const [content, setContent] = useState<string>('');
  const [modifiedContent, setModifiedContent] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisStage, setAnalysisStage] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [previousAnalysisResult, setPreviousAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>('');
  
  // State for suggestions
  const [reportSuggestions, setReportSuggestions] = useState<Suggestion[]>([]);
  const [appliedSuggestions, setAppliedSuggestions] = useState<Record<string, boolean>>({});
  const [showReanalyzePrompt, setShowReanalyzePrompt] = useState<boolean>(false);
  
  // State for comparison
  const [showComparison, setShowComparison] = useState<boolean>(false);
  const [previousIssueCount, setPreviousIssueCount] = useState<number>(0);
  const [currentIssueCount, setCurrentIssueCount] = useState<number>(0);
  const [previousSuggestionCount, setPreviousSuggestionCount] = useState<number>(0);
  const [currentSuggestionCount, setCurrentSuggestionCount] = useState<number>(0);

  // Extract suggestions from the analysis report
  const extractSuggestionsFromReport = (report: string): Suggestion[] => {
    // First try to find the Improvement Suggestions section
    const improvementSectionRegex = /\*\*4\. Improvement Suggestions\*\*([\s\S]*?)(?:\*\*\d|$)/;
    const match = report.match(improvementSectionRegex);
    
    if (!match || !match[1]) {
      // If no match, create some example suggestions for testing
      console.log('No improvement suggestions found in report, using examples');
      return [
        {
          id: 'suggestion-1',
          original_text: 'fabulous souls',
          suggested_text: 'fashion-forward individuals',
          explanation: 'Use more professional terminology',
        },
        {
          id: 'suggestion-2',
          original_text: 'ultimate sidekicks',
          suggested_text: 'perfect companions',
          explanation: 'More elegant phrasing',
        },
        {
          id: 'suggestion-3',
          original_text: '💃',
          suggested_text: '',
          explanation: 'Reduce emoji usage',
        }
      ];
    }
    
    const improvementSection = match[1];
    // Updated regex to better match the format in the report - using 'g' flag only for ES2015 compatibility
    const bulletPointRegex = /-\s+\*\*(.*?)\*\*:\s*(.*?)(?=\s*-\s*\*\*|$)/g;
    const suggestions: Suggestion[] = [];
    
    let bulletMatch;
    while ((bulletMatch = bulletPointRegex.exec(improvementSection)) !== null) {
      const original = bulletMatch[1];
      const suggestion = bulletMatch[2];
      
      suggestions.push({
        id: `suggestion-${suggestions.length + 1}`,
        original_text: original.trim(),
        suggested_text: suggestion.trim(),
        explanation: `Replace "${original}" with "${suggestion}"`,
      });
    }
    
    // If no suggestions were extracted but we found the section, add example suggestions
    if (suggestions.length === 0) {
      console.log('Failed to extract suggestions from section, using examples');
      return [
        {
          id: 'suggestion-1',
          original_text: 'fabulous souls',
          suggested_text: 'fashion-forward individuals',
          explanation: 'Use more professional terminology',
        },
        {
          id: 'suggestion-2',
          original_text: 'ultimate sidekicks',
          suggested_text: 'perfect companions',
          explanation: 'More elegant phrasing',
        }
      ];
    }
    
    return suggestions;
  };

  // Calculate issue and suggestion counts from the report
  const calculateCounts = (report: string): { issueCount: number; suggestionCount: number } => {
    const issueMatch = report.match(/\*\*Total Issues:\*\*\s*(\d+)/i);
    const suggestionMatch = report.match(/\*\*Total Suggestions:\*\*\s*(\d+)/i);
    
    return {
      issueCount: issueMatch ? parseInt(issueMatch[1], 10) : 0,
      suggestionCount: suggestionMatch ? parseInt(suggestionMatch[1], 10) : 0
    };
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim() || isAnalyzing) return;
    
    setError('');
    setIsAnalyzing(true);
    
    // Save previous analysis result for comparison if available
    if (analysisResult) {
      setPreviousAnalysisResult(analysisResult);
      setShowComparison(true);
      
      // Calculate previous counts
      const counts = calculateCounts(analysisResult.report);
      setPreviousIssueCount(counts.issueCount);
      setPreviousSuggestionCount(counts.suggestionCount);
    }
    
    try {
      // Simulate analysis stages
      setAnalysisStage('analyzing');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setAnalysisStage('processing');
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setAnalysisStage('finalizing');
      
      // Call the API
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
      } else {
        setError(response.error || 'Failed to analyze content. Please try again.');
      }
    } catch (err) {
      setError('An error occurred during analysis. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
      setAnalysisStage('');
    }
  };

  // Apply a suggestion to the content
  const applyReportSuggestion = (suggestion: Suggestion) => {
    if (isAnalyzing) return;
    
    const newContent = modifiedContent.replace(
      suggestion.original_text,
      suggestion.suggested_text
    );
    
    setModifiedContent(newContent);
    setContent(newContent);
    
    // Mark suggestion as applied
    setAppliedSuggestions(prev => ({
      ...prev,
      [suggestion.id]: true
    }));
    
    setShowReanalyzePrompt(true);
  };

  // Handle re-analysis after applying suggestions
  const handleReanalyze = () => {
    setShowReanalyzePrompt(false);
    handleSubmit(new Event('submit') as unknown as React.FormEvent);
  };

  // Reset applied suggestions
  const resetSuggestions = () => {
    setContent(modifiedContent);
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
      <div className="h-full flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
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
        
        {/* Scrollable Content */}
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
          {isAnalyzing && (
            <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-md">
              <div className="flex items-center">
                <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                <span>
                  {analysisStage === 'analyzing' && 'Analyzing content...'}
                  {analysisStage === 'processing' && 'Processing analysis results...'}
                  {analysisStage === 'finalizing' && 'Finalizing report...'}
                  {!analysisStage && 'Analyzing...'}
                </span>
              </div>
              <div className="mt-2 w-full bg-blue-200 rounded-full h-1.5">
                <div 
                  className="bg-blue-600 h-1.5 rounded-full transition-all duration-300" 
                  style={{ 
                    width: analysisStage === 'analyzing' ? '33%' : 
                           analysisStage === 'processing' ? '66%' : 
                           analysisStage === 'finalizing' ? '90%' : '10%' 
                  }}
                ></div>
              </div>
            </div>
          )}
          
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
            
            {/* Removed re-analyze prompt from here - moved to suggestions section */}
            
            {/* Analyze Button */}
            <div className="flex justify-end mt-4">
              <button
                type="submit"
                className="px-6 py-3 rounded-md flex items-center shadow-md"
                style={{
                  backgroundColor: '#6D3BEB', // Primary purple from Tailwind config
                  color: 'white',
                  fontWeight: 500,
                }}
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
          
          {/* Analysis Results */}
          {analysisResult && (
            <div className="space-y-6 mt-6">
              {/* Brand Voice Alignment Scores */}
              <div className="bg-white border border-gray-200 rounded-md p-4">
                <h3 className="text-md font-medium mb-3">Brand Voice Alignment Scores</h3>
                
                {/* Score Comparison */}
                {showComparison && previousAnalysisResult && (
                  <div className="mb-4 p-3 bg-gray-50 rounded-md">
                    <h4 className="text-sm font-medium mb-2">Comparison with Previous Analysis</h4>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600 mb-1">Overall Score:</p>
                        <div className="flex items-center">
                          <span className="font-medium">{(previousAnalysisResult.overall_score * 100).toFixed(0)}%</span>
                          <span className="mx-2">→</span>
                          <span className="font-medium">{(analysisResult.overall_score * 100).toFixed(0)}%</span>
                          
                          {analysisResult.overall_score > previousAnalysisResult.overall_score ? (
                            <span className="ml-2 text-green-600 flex items-center">
                              <ThumbsUp size={14} className="mr-1" />
                              +{((analysisResult.overall_score - previousAnalysisResult.overall_score) * 100).toFixed(0)}%
                            </span>
                          ) : analysisResult.overall_score < previousAnalysisResult.overall_score ? (
                            <span className="ml-2 text-red-600 flex items-center">
                              <ThumbsDown size={14} className="mr-1" />
                              {((analysisResult.overall_score - previousAnalysisResult.overall_score) * 100).toFixed(0)}%
                            </span>
                          ) : (
                            <span className="ml-2 text-gray-600">No change</span>
                          )}
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-gray-600 mb-1">Issues:</p>
                        <div className="flex items-center">
                          <span className="font-medium">{previousIssueCount}</span>
                          <span className="mx-2">→</span>
                          <span className="font-medium">{currentIssueCount}</span>
                          
                          {previousIssueCount > currentIssueCount ? (
                            <span className="ml-2 text-green-600 flex items-center">
                              <ThumbsUp size={14} className="mr-1" />
                              -{previousIssueCount - currentIssueCount}
                            </span>
                          ) : previousIssueCount < currentIssueCount ? (
                            <span className="ml-2 text-red-600 flex items-center">
                              <ThumbsDown size={14} className="mr-1" />
                              +{currentIssueCount - previousIssueCount}
                            </span>
                          ) : (
                            <span className="ml-2 text-gray-600">No change</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Score Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm text-gray-600 mb-1">Overall Score</p>
                    <p className="text-2xl font-bold text-primary-600">{(analysisResult.overall_score * 100).toFixed(0)}%</p>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm text-gray-600 mb-1">Personality</p>
                    <p className="text-2xl font-bold text-primary-600">{(analysisResult.personality_score * 100).toFixed(0)}%</p>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm text-gray-600 mb-1">Tonality</p>
                    <p className="text-2xl font-bold text-primary-600">{(analysisResult.tonality_score * 100).toFixed(0)}%</p>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm text-gray-600 mb-1">Do's Alignment</p>
                    <p className="text-2xl font-bold text-primary-600">{(analysisResult.dos_alignment * 100).toFixed(0)}%</p>
                  </div>
                </div>
              </div>
              
              {/* Suggestions - Always displayed */}
              <div className="bg-white border border-gray-200 rounded-md p-4">
                <h3 className="text-md font-medium mb-3">Improvement Suggestions</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Click on a suggestion to apply it to your content.
                </p>
                
                {reportSuggestions.length > 0 ? (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {reportSuggestions.map((suggestion) => (
                      <button
                        key={suggestion.id}
                        onClick={() => applyReportSuggestion(suggestion)}
                        className={cn(
                          "px-3 py-2 rounded-md text-sm flex items-center transition-colors",
                          appliedSuggestions[suggestion.id]
                            ? "bg-green-100 text-green-800 border border-green-200"
                            : "bg-blue-50 text-blue-800 border border-blue-100 hover:bg-blue-100"
                        )}
                        disabled={isAnalyzing}
                      >
                        {appliedSuggestions[suggestion.id] ? (
                          <Check size={14} className="mr-1" />
                        ) : (
                          <Wand2 size={14} className="mr-1" />
                        )}
                        <span>
                          {suggestion.suggested_text.length > 30
                            ? suggestion.suggested_text.substring(0, 30) + "..."
                            : suggestion.suggested_text}
                        </span>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="bg-gray-50 p-4 rounded-md text-gray-500 text-center mb-4">
                    <Wand2 size={18} className="mx-auto mb-2" />
                    <p>No suggestions available for this content.</p>
                  </div>
                )}
                
                {/* Re-analyze prompt - Moved here from the form section */}
                {showReanalyzePrompt && (
                  <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-md mt-4">
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
              </div>
              
              {/* Content Display */}
              <div className="bg-white border border-gray-200 rounded-md p-4">
                <h3 className="text-md font-medium mb-3">
                  {modifiedContent !== content ? 'Modified Content' : 'Original Content'}
                </h3>
                <div className="prose prose-sm max-w-none bg-gray-50 p-3 rounded-md">
                  <p>{modifiedContent}</p>
                </div>
                <div className="mt-2 flex justify-end">
                  <button
                    type="button"
                    onClick={() => {
                      navigator.clipboard.writeText(modifiedContent);
                    }}
                    className="text-sm text-gray-600 flex items-center hover:text-gray-900"
                  >
                    <Copy size={14} className="mr-1" />
                    Copy to clipboard
                  </button>
                </div>
              </div>
              
              {/* Detailed Report */}
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
    </div>
  );
};

export default AnalyzerPanel;

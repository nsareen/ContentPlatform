/**
 * Utility functions for working with brand voice analysis reports
 */

/**
 * Extract suggestions from an analysis report
 */
export const extractSuggestionsFromReport = (report: string): {id: string, text: string}[] => {
  if (!report) return [];
  
  const suggestions: {id: string, text: string}[] = [];
  
  // Method 1: Look for specific sections
  const improvementSectionRegex = /\*\*4\. Improvement Suggestions\*\*([\s\S]*?)(?:\*\*\d|$)/;
  const improvementMatch = report.match(improvementSectionRegex);
  
  if (improvementMatch && improvementMatch[1]) {
    // Extract bullet points with the format: - **Title**: Description
    const bulletPointRegex = /-\s+\*\*(.*?)\*\*:\s*(.*?)(?=\s*-\s*\*\*|$)/g;
    const content = improvementMatch[1];
    let bulletMatch;
    
    // Extract all bullet points
    while ((bulletMatch = bulletPointRegex.exec(content)) !== null) {
      if (bulletMatch[1]) {
        suggestions.push({
          id: `report-suggestion-${suggestions.length}`,
          text: bulletMatch[1].trim()
        });
      }
    }
  }
  
  // Method 2: Fallback - direct pattern matching for common suggestion formats
  if (suggestions.length === 0) {
    // Look for patterns like "Moderate Use of Emojis", "Incorporate Product Details", etc.
    const commonPatterns = [
      { regex: /Moderate\s+Use\s+of\s+Emojis/i, text: "Moderate Use of Emojis" },
      { regex: /Incorporate\s+Product\s+Details/i, text: "Incorporate Product Details" },
      { regex: /Refine\s+Messaging/i, text: "Refine Messaging" },
      { regex: /Clear\s+Value\s+Proposition/i, text: "Clear Value Proposition" },
      { regex: /Reduce\s+Exclamations/i, text: "Reduce Exclamations" },
      { regex: /Add\s+Specificity/i, text: "Add Specificity" },
      { regex: /Focus\s+on\s+Benefits/i, text: "Focus on Benefits" },
      { regex: /Maintain\s+Consistency/i, text: "Maintain Consistency" }
    ];
    
    commonPatterns.forEach((pattern, index) => {
      if (pattern.regex.test(report)) {
        suggestions.push({
          id: `direct-suggestion-${index}`,
          text: pattern.text
        });
      }
    });
  }
  
  // Method 3: Extract from Key Issues as a last resort
  if (suggestions.length === 0) {
    const issuesMatch = report.match(/\*\*3\. Key Issues\*\*([\s\S]*?)(?:\*\*\d|$)/);
    if (issuesMatch && issuesMatch[1]) {
      // Look for bullet points in the Key Issues section
      const issueRegex = /-\s+\*\*(.*?)\*\*:?\s*(.*?)(?=\s*-\s*\*\*|$)/g;
      const content = issuesMatch[1];
      let issueMatch;
      
      while ((issueMatch = issueRegex.exec(content)) !== null) {
        if (issueMatch[1]) {
          const title = issueMatch[1].trim();
          suggestions.push({
            id: `issue-${suggestions.length}`,
            text: `Fix ${title}`
          });
        }
      }
    }
  }
  
  // Method 4: Hardcoded fallback suggestions if nothing else worked
  if (suggestions.length === 0) {
    // Add some default suggestions based on common brand voice issues
    suggestions.push(
      { id: 'default-1', text: 'Moderate Use of Emojis' },
      { id: 'default-2', text: 'Incorporate Product Details' },
      { id: 'default-3', text: 'Refine Messaging' }
    );
  }
  
  return suggestions;
};

/**
 * Calculate issue and suggestion counts from a report
 */
export const calculateCounts = (report: string) => {
  // Extract issue count
  const getIssueCount = (report: string) => {
    const issuesMatch = report.match(/\*\*3\. Key Issues\*\*([\s\S]*?)(?:\*\*4\.|$)/);
    if (!issuesMatch || !issuesMatch[1]) return 0;
    
    const bulletPoints = issuesMatch[1].match(/-\s+\*\*/g);
    return bulletPoints ? bulletPoints.length : 0;
  };
  
  // Extract suggestion count
  const getSuggestionCount = (report: string) => {
    const suggestionsMatch = report.match(/\*\*4\. Improvement Suggestions\*\*([\s\S]*?)(?:\*\*5\.|$)/);
    if (!suggestionsMatch || !suggestionsMatch[1]) return 0;
    
    const bulletPoints = suggestionsMatch[1].match(/-\s+\*\*/g);
    return bulletPoints ? bulletPoints.length : 0;
  };
  
  return {
    issueCount: getIssueCount(report),
    suggestionCount: getSuggestionCount(report)
  };
};

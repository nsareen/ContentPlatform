"""
Node implementations for the Brand Voice Analysis agent.
"""

import json
import uuid
from typing import Dict, List, Any, Callable, Tuple, Optional

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.agents.brand_voice_analysis.state import (
    BrandVoiceAnalysisState,
    ContentIssue,
    ContentSuggestion,
    IssueType,
    SuggestionCategory,
    AnalysisDepth
)
from app.agents.brand_voice_analysis.prompts import (
    CONTENT_ANALYZER_PROMPT,
    EVIDENCE_COLLECTOR_PROMPT,
    SCORE_CALCULATOR_PROMPT,
    SUGGESTION_GENERATOR_PROMPT,
    ANALYSIS_REPORT_PROMPT
)
from app.agents.config import get_llm


class ContentAnalyzerNode:
    """Node that analyzes content against brand voice guidelines."""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
    
    async def __call__(self, state: BrandVoiceAnalysisState) -> BrandVoiceAnalysisState:
        """Analyze content against brand voice guidelines."""
        try:
            # Extract brand voice details
            brand_voice = state["brand_voice"]
            content = state["content"]
            options = state.get("options", {})
            analysis_depth = options.get("analysis_depth", "standard")
            
            # Create system prompt
            system_prompt = CONTENT_ANALYZER_PROMPT.format(
                personality=brand_voice.get("voice_metadata", {}).get("personality", "Not specified"),
                tonality=brand_voice.get("voice_metadata", {}).get("tonality", "Not specified"),
                dos=brand_voice.get("dos", "Not specified"),
                donts=brand_voice.get("donts", "Not specified"),
                analysis_depth=analysis_depth
            )
            
            # Create messages for LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Please analyze this content: {content}")
            ]
            
            # Get response from LLM
            response = await self.llm.ainvoke(messages)
            
            # Parse issues from response
            issues = self._parse_issues(response.content)
            
            # Update state
            state["issues"] = [issue.dict() for issue in issues]
            state["analysis_stage"] = "content_analyzed"
            
            # Add messages to state for debugging/logging
            if "messages" not in state:
                state["messages"] = []
            state["messages"].append({
                "role": "system",
                "content": f"Content analyzed. Found {len(issues)} issues."
            })
            
            return state
        except Exception as e:
            # Handle errors
            state["error"] = f"Error in content analyzer: {str(e)}"
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Error in content analyzer: {str(e)}"
            }]
            return state
    
    def _parse_issues(self, response_text: str) -> List[ContentIssue]:
        """Parse issues from LLM response."""
        issues = []
        
        # Simple parsing logic - this could be enhanced with better structured output parsing
        lines = response_text.split("\n")
        current_issue = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for issue markers
            if line.lower().startswith(("issue:", "problem:", "mismatch:", "violation:")):
                # Save previous issue if exists
                if current_issue:
                    issues.append(current_issue)
                
                # Start new issue
                current_issue = ContentIssue(
                    start_index=0,  # Will be refined in evidence collection
                    end_index=0,    # Will be refined in evidence collection
                    text="",        # Will be added below
                    issue_type=self._determine_issue_type(line),
                    explanation="",
                    severity=0.5
                )
            
            # Add text to current issue
            if current_issue:
                if "text:" in line.lower():
                    current_issue.text = line.split("text:", 1)[1].strip()
                elif "explanation:" in line.lower():
                    current_issue.explanation = line.split("explanation:", 1)[1].strip()
                elif not current_issue.explanation and current_issue.text:
                    # If we have text but no explanation yet, assume this line is the explanation
                    current_issue.explanation = line
        
        # Add the last issue if exists
        if current_issue and current_issue.text:
            issues.append(current_issue)
            
        return issues
    
    def _determine_issue_type(self, line: str) -> IssueType:
        """Determine the issue type based on the line text."""
        line_lower = line.lower()
        
        if "personality" in line_lower:
            return IssueType.PERSONALITY_MISMATCH
        elif "tone" in line_lower or "tonality" in line_lower:
            return IssueType.TONALITY_MISMATCH
        elif "do" in line_lower and "not" in line_lower:
            return IssueType.DONTS_VIOLATION
        elif "do" in line_lower:
            return IssueType.DOS_VIOLATION
        elif "style" in line_lower:
            return IssueType.STYLE_INCONSISTENCY
        else:
            return IssueType.GENERAL


class EvidenceCollectorNode:
    """Node that collects evidence for issues identified in content."""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
    
    async def __call__(self, state: BrandVoiceAnalysisState) -> BrandVoiceAnalysisState:
        """Collect evidence for issues identified in content."""
        try:
            # Check if we have issues to collect evidence for
            if not state.get("issues"):
                state["messages"] = state.get("messages", []) + [{
                    "role": "system",
                    "content": "No issues to collect evidence for."
                }]
                state["evidence"] = {}
                state["analysis_stage"] = "evidence_collected"
                return state
            
            # Extract brand voice details and content
            brand_voice = state["brand_voice"]
            content = state["content"]
            issues = state["issues"]
            
            # Create system prompt
            system_prompt = EVIDENCE_COLLECTOR_PROMPT.format(
                personality=brand_voice.get("voice_metadata", {}).get("personality", "Not specified"),
                tonality=brand_voice.get("voice_metadata", {}).get("tonality", "Not specified"),
                dos=brand_voice.get("dos", "Not specified"),
                donts=brand_voice.get("donts", "Not specified")
            )
            
            # Create messages for LLM
            issues_text = "\n".join([f"Issue {i+1}: {issue['text']} - {issue['issue_type']}" 
                                    for i, issue in enumerate(issues)])
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Content to analyze: {content}\n\nIssues identified:\n{issues_text}\n\nPlease collect evidence for each issue.")
            ]
            
            # Get response from LLM
            response = await self.llm.ainvoke(messages)
            
            # Process response to extract evidence
            evidence = self._extract_evidence(response.content, issues, content)
            
            # Update state
            state["evidence"] = evidence
            state["analysis_stage"] = "evidence_collected"
            
            # Update issues with more precise information
            updated_issues = []
            for i, issue in enumerate(issues):
                issue_evidence = evidence.get(f"issue_{i+1}", [])
                if issue_evidence:
                    # Update issue with more precise information if available
                    issue["start_index"] = self._find_text_position(content, issue["text"])
                    issue["end_index"] = issue["start_index"] + len(issue["text"]) if issue["start_index"] >= 0 else -1
                    issue["severity"] = self._calculate_severity(issue_evidence)
                updated_issues.append(issue)
            
            state["issues"] = updated_issues
            
            # Add messages to state for debugging/logging
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Evidence collected for {len(issues)} issues."
            }]
            
            return state
        except Exception as e:
            # Handle errors
            state["error"] = f"Error in evidence collector: {str(e)}"
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Error in evidence collector: {str(e)}"
            }]
            return state
    
    def _extract_evidence(self, response_text: str, issues: List[Dict[str, Any]], content: str) -> Dict[str, List[str]]:
        """Extract evidence from LLM response."""
        evidence = {}
        
        # Simple parsing logic
        lines = response_text.split("\n")
        current_issue = None
        current_evidence = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for issue markers
            if line.lower().startswith(("issue", "evidence for issue")):
                # Save previous evidence if exists
                if current_issue and current_evidence:
                    evidence[current_issue] = current_evidence
                
                # Start new issue evidence
                for i in range(len(issues)):
                    if f"issue {i+1}" in line.lower() or f"issue #{i+1}" in line.lower():
                        current_issue = f"issue_{i+1}"
                        current_evidence = []
                        break
            
            # Add evidence to current issue
            elif current_issue and not line.lower().startswith(("issue", "evidence")):
                current_evidence.append(line)
        
        # Add the last evidence if exists
        if current_issue and current_evidence:
            evidence[current_issue] = current_evidence
            
        return evidence
    
    def _find_text_position(self, content: str, text: str) -> int:
        """Find the position of text in content."""
        return content.find(text)
    
    def _calculate_severity(self, evidence: List[str]) -> float:
        """Calculate severity based on evidence."""
        # Simple heuristic - look for severity indicators in evidence
        severity_indicators = {
            "critical": 1.0,
            "major": 0.8,
            "significant": 0.7,
            "moderate": 0.5,
            "minor": 0.3,
            "slight": 0.2,
            "minimal": 0.1
        }
        
        # Default severity
        severity = 0.5
        
        # Check for explicit severity mentions
        for line in evidence:
            line_lower = line.lower()
            if "severity:" in line_lower:
                # Try to extract numeric severity
                try:
                    severity_text = line_lower.split("severity:", 1)[1].strip()
                    if severity_text[0].isdigit():
                        # Handle numeric severity (assuming 0-10 or 0-1 scale)
                        numeric_severity = float(severity_text.split()[0])
                        if numeric_severity > 1:  # If on a 0-10 scale
                            severity = numeric_severity / 10
                        else:
                            severity = numeric_severity
                        return min(1.0, max(0.0, severity))  # Ensure in range [0,1]
                except:
                    pass
                
                # Check for text-based severity indicators
                for indicator, value in severity_indicators.items():
                    if indicator in line_lower:
                        return value
        
        return severity


class ScoreCalculatorNode:
    """Node that calculates scores based on content analysis and evidence."""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
    
    async def __call__(self, state: BrandVoiceAnalysisState) -> BrandVoiceAnalysisState:
        """Calculate scores based on content analysis and evidence."""
        try:
            # Extract brand voice details
            brand_voice = state["brand_voice"]
            content = state["content"]
            issues = state.get("issues", [])
            evidence = state.get("evidence", {})
            
            # Create system prompt
            system_prompt = SCORE_CALCULATOR_PROMPT.format(
                personality=brand_voice.get("voice_metadata", {}).get("personality", "Not specified"),
                tonality=brand_voice.get("voice_metadata", {}).get("tonality", "Not specified"),
                dos=brand_voice.get("dos", "Not specified"),
                donts=brand_voice.get("donts", "Not specified")
            )
            
            # Create messages for LLM
            issues_text = "\n".join([f"Issue {i+1}: {issue['text']} - {issue['issue_type']} (Severity: {issue.get('severity', 0.5)})" 
                                    for i, issue in enumerate(issues)])
            
            evidence_text = ""
            for issue_key, evidence_list in evidence.items():
                evidence_text += f"\n{issue_key.replace('_', ' ').title()}:\n"
                evidence_text += "\n".join([f"- {e}" for e in evidence_list])
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Content length: {len(content)} characters\n\nIssues identified ({len(issues)}):\n{issues_text}\n\nEvidence:{evidence_text}\n\nPlease calculate alignment scores.")
            ]
            
            # Get response from LLM
            response = await self.llm.ainvoke(messages)
            
            # Parse scores from response
            scores = self._parse_scores(response.content)
            
            # Update state
            state["scores"] = scores
            state["analysis_stage"] = "scores_calculated"
            
            # Add messages to state for debugging/logging
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Scores calculated: Overall={scores.get('overall', 'N/A')}"
            }]
            
            return state
        except Exception as e:
            # Handle errors
            state["error"] = f"Error in score calculator: {str(e)}"
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Error in score calculator: {str(e)}"
            }]
            return state
    
    def _parse_scores(self, response_text: str) -> Dict[str, float]:
        """Parse scores from LLM response."""
        scores = {}
        score_types = ["overall", "personality", "tonality", "dos", "don'ts", "donts"]
        
        # Simple parsing logic
        lines = response_text.split("\n")
        
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue
                
            # Look for score indicators
            for score_type in score_types:
                if f"{score_type} score" in line or f"{score_type}:" in line:
                    # Try to extract numeric score
                    try:
                        # Find the numeric value in the line
                        parts = line.replace(f"{score_type} score", "").replace(f"{score_type}:", "").strip().split()
                        for part in parts:
                            if part[0].isdigit():
                                numeric_score = float(part)
                                # Handle different scales
                                if numeric_score > 1 and numeric_score <= 10:  # If on a 0-10 scale
                                    numeric_score /= 10
                                elif numeric_score > 10 and numeric_score <= 100:  # If on a 0-100 scale
                                    numeric_score /= 100
                                
                                # Normalize score type key
                                score_key = score_type.replace("'", "")
                                scores[score_key] = min(1.0, max(0.0, numeric_score))  # Ensure in range [0,1]
                                break
                    except:
                        continue
        
        # Ensure we have all required scores with defaults if missing
        required_scores = ["overall", "personality", "tonality", "dos", "donts"]
        for score in required_scores:
            if score not in scores:
                # If we have some scores, estimate the missing ones
                if scores:
                    scores[score] = sum(scores.values()) / len(scores)
                else:
                    # Default if we couldn't parse any scores
                    scores[score] = 0.5
        
        return scores


class SuggestionGeneratorNode:
    """Node that generates suggestions for improving content alignment with brand voice."""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
    
    async def __call__(self, state: BrandVoiceAnalysisState) -> BrandVoiceAnalysisState:
        """Generate suggestions for improving content alignment with brand voice."""
        try:
            # Check if suggestions are requested
            options = state.get("options", {})
            if not options.get("include_suggestions", True):
                state["suggestions"] = []
                state["analysis_stage"] = "suggestions_generated"
                state["messages"] = state.get("messages", []) + [{
                    "role": "system",
                    "content": "Suggestions generation skipped as per options."
                }]
                return state
            
            # Extract brand voice details
            brand_voice = state["brand_voice"]
            content = state["content"]
            issues = state.get("issues", [])
            
            # Skip if no issues found
            if not issues:
                state["suggestions"] = []
                state["analysis_stage"] = "suggestions_generated"
                state["messages"] = state.get("messages", []) + [{
                    "role": "system",
                    "content": "No issues found, so no suggestions generated."
                }]
                return state
            
            # Create system prompt
            system_prompt = SUGGESTION_GENERATOR_PROMPT.format(
                personality=brand_voice.get("voice_metadata", {}).get("personality", "Not specified"),
                tonality=brand_voice.get("voice_metadata", {}).get("tonality", "Not specified"),
                dos=brand_voice.get("dos", "Not specified"),
                donts=brand_voice.get("donts", "Not specified")
            )
            
            # Create messages for LLM
            issues_text = "\n".join([f"Issue {i+1}: {issue['text']} - {issue['issue_type']} (Severity: {issue.get('severity', 0.5)})" 
                                    for i, issue in enumerate(issues)])
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Content: {content}\n\nIssues identified:\n{issues_text}\n\nPlease generate improvement suggestions.")
            ]
            
            # Get response from LLM
            response = await self.llm.ainvoke(messages)
            
            # Parse suggestions from response
            suggestions = self._parse_suggestions(response.content, issues)
            
            # Limit suggestions if needed
            max_suggestions = options.get("max_suggestions", 5)
            if len(suggestions) > max_suggestions:
                # Sort by priority (lower number = higher priority)
                suggestions.sort(key=lambda x: x.priority)
                suggestions = suggestions[:max_suggestions]
            
            # Update state
            state["suggestions"] = [suggestion.dict() for suggestion in suggestions]
            state["analysis_stage"] = "suggestions_generated"
            
            # Add messages to state for debugging/logging
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Generated {len(suggestions)} suggestions for improvement."
            }]
            
            return state
        except Exception as e:
            # Handle errors
            state["error"] = f"Error in suggestion generator: {str(e)}"
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Error in suggestion generator: {str(e)}"
            }]
            return state
    
    def _parse_suggestions(self, response_text: str, issues: List[Dict[str, Any]]) -> List[ContentSuggestion]:
        """Parse suggestions from LLM response."""
        suggestions = []
        
        # Simple parsing logic
        lines = response_text.split("\n")
        current_suggestion = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for suggestion markers
            if line.lower().startswith(("suggestion", "improvement", "recommendation")):
                # Save previous suggestion if exists
                if current_suggestion and current_suggestion.original_text and current_suggestion.suggested_text:
                    suggestions.append(current_suggestion)
                
                # Start new suggestion
                current_suggestion = ContentSuggestion(
                    id=str(uuid.uuid4()),
                    original_text="",
                    suggested_text="",
                    explanation="",
                    category=SuggestionCategory.GENERAL,
                    priority=2  # Default medium priority
                )
            
            # Add details to current suggestion
            if current_suggestion:
                line_lower = line.lower()
                
                if "original:" in line_lower or "original text:" in line_lower:
                    current_suggestion.original_text = line.split(":", 1)[1].strip()
                elif "suggested:" in line_lower or "suggested text:" in line_lower or "replacement:" in line_lower:
                    current_suggestion.suggested_text = line.split(":", 1)[1].strip()
                elif "explanation:" in line_lower or "reason:" in line_lower:
                    current_suggestion.explanation = line.split(":", 1)[1].strip()
                elif "category:" in line_lower:
                    category_text = line.split(":", 1)[1].strip().lower()
                    for cat in SuggestionCategory:
                        if cat.value in category_text:
                            current_suggestion.category = cat
                            break
                elif "priority:" in line_lower:
                    priority_text = line.split(":", 1)[1].strip().lower()
                    if "high" in priority_text or "1" in priority_text:
                        current_suggestion.priority = 1
                    elif "medium" in priority_text or "2" in priority_text:
                        current_suggestion.priority = 2
                    elif "low" in priority_text or "3" in priority_text:
                        current_suggestion.priority = 3
                elif not current_suggestion.explanation and current_suggestion.original_text and current_suggestion.suggested_text:
                    # If we have original and suggested text but no explanation yet, assume this line is the explanation
                    current_suggestion.explanation = line
        
        # Add the last suggestion if exists
        if current_suggestion and current_suggestion.original_text and current_suggestion.suggested_text:
            suggestions.append(current_suggestion)
            
        return suggestions


class AnalysisReportNode:
    """Node that generates the final analysis report."""
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
    
    async def __call__(self, state: BrandVoiceAnalysisState) -> BrandVoiceAnalysisState:
        """Generate the final analysis report."""
        try:
            # Extract analysis results
            brand_voice = state["brand_voice"]
            content = state["content"]
            issues = state.get("issues", [])
            suggestions = state.get("suggestions", [])
            scores = state.get("scores", {})
            
            # Create the analysis result structure
            analysis_result = {
                "overall_score": scores.get("overall", 0.5),
                "personality_score": scores.get("personality", 0.5),
                "tonality_score": scores.get("tonality", 0.5),
                "dos_alignment": scores.get("dos", 0.5),
                "donts_alignment": scores.get("donts", 0.5),
                "highlighted_sections": issues,
                "suggestions": suggestions,
                "analysis_metadata": {
                    "brand_voice_id": brand_voice.get("id", ""),
                    "brand_voice_name": brand_voice.get("name", ""),
                    "content_length": len(content),
                    "issue_count": len(issues),
                    "suggestion_count": len(suggestions),
                    "timestamp": str(uuid.uuid1())
                }
            }
            
            # Generate a human-readable report if needed
            if state.get("options", {}).get("generate_report", True):
                report = await self._generate_report(
                    content=content,
                    brand_voice=brand_voice,
                    issues=issues,
                    suggestions=suggestions,
                    scores=scores
                )
                analysis_result["report"] = report
            
            # Update state
            state["analysis_result"] = analysis_result
            state["analysis_stage"] = "completed"
            
            # Add messages to state for debugging/logging
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Analysis completed with overall score: {scores.get('overall', 0.5)}"
            }]
            
            return state
        except Exception as e:
            # Handle errors
            state["error"] = f"Error in analysis report generator: {str(e)}"
            state["messages"] = state.get("messages", []) + [{
                "role": "system",
                "content": f"Error in analysis report generator: {str(e)}"
            }]
            return state
    
    async def _generate_report(self, content: str, brand_voice: Dict[str, Any], 
                              issues: List[Dict[str, Any]], suggestions: List[Dict[str, Any]], 
                              scores: Dict[str, float]) -> str:
        """Generate a human-readable analysis report."""
        # Create system prompt
        system_prompt = ANALYSIS_REPORT_PROMPT
        
        # Prepare data for the report
        content_preview = content[:500] + "..." if len(content) > 500 else content
        
        scores_text = "\n".join([f"{k.title()} Score: {v}" for k, v in scores.items()])
        
        issues_text = ""
        for i, issue in enumerate(issues[:5]):  # Limit to top 5 issues
            issues_text += f"\n{i+1}. {issue['text']} - {issue['issue_type']}\n   Explanation: {issue['explanation']}"
        
        suggestions_text = ""
        for i, suggestion in enumerate(suggestions[:5]):  # Limit to top 5 suggestions
            suggestions_text += f"\n{i+1}. Original: \"{suggestion['original_text']}\"\n   Suggested: \"{suggestion['suggested_text']}\"\n   Explanation: {suggestion['explanation']}"
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Brand Voice: {brand_voice['name']}\n\nContent Preview: {content_preview}\n\nScores:\n{scores_text}\n\nKey Issues:{issues_text}\n\nSuggestions:{suggestions_text}\n\nPlease generate a comprehensive analysis report.")
        ]
        
        # Get response from LLM
        response = await self.llm.ainvoke(messages)
        
        return response.content

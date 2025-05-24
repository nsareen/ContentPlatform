"""
Node implementations for the Brand Voice Analyzer.
"""

import json
import uuid
from typing import Dict, List, Any, Callable, Tuple, Optional

from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from app.agents.brand_voice_analyzer.state import (
    BrandVoiceAnalyzerState,
    IssueType,
    SuggestionCategory,
    AnalysisDepth
)
from app.agents.brand_voice_analyzer.prompts import (
    CONTENT_ANALYZER_PROMPT,
    EVIDENCE_COLLECTOR_PROMPT,
    SCORE_CALCULATOR_PROMPT,
    SUGGESTION_GENERATOR_PROMPT,
    ANALYSIS_REPORT_PROMPT
)
from app.agents.config import get_llm


def classify_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Determine the intent of the analysis request."""
    # For brand voice analysis, the intent is always "analyze"
    state["intent"] = "analyze"
    return state


def analyze_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze content against brand voice guidelines."""
    try:
        # Get the LLM
        llm = get_llm()
        
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
        response = llm.invoke(messages)
        
        # Parse issues from response
        issues = parse_issues(response.content)
        
        # Update state
        state["issues"] = issues
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


def parse_issues(response_text: str) -> List[Dict[str, Any]]:
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
            issue_text = line.split(":", 1)[1].strip() if ":" in line else line
            current_issue = {
                "id": str(uuid.uuid4()),
                "start_index": 0,  # Will be refined in evidence collection
                "end_index": 0,    # Will be refined in evidence collection
                "text": issue_text,
                "issue_type": determine_issue_type(line),
                "explanation": "",
                "severity": 0.5    # Default severity
            }
        elif current_issue and "explanation:" in line.lower():
            # Add explanation to current issue
            current_issue["explanation"] = line.split(":", 1)[1].strip() if ":" in line else line
        elif current_issue:
            # Add to current issue explanation if no specific marker
            if current_issue["explanation"]:
                current_issue["explanation"] += " " + line
            else:
                current_issue["explanation"] = line
    
    # Add the last issue if exists
    if current_issue:
        issues.append(current_issue)
    
    return issues


def determine_issue_type(line: str) -> str:
    """Determine the issue type based on the line text."""
    line_lower = line.lower()
    
    if "personality" in line_lower:
        return IssueType.PERSONALITY_MISMATCH
    elif "tone" in line_lower or "tonality" in line_lower:
        return IssueType.TONALITY_MISMATCH
    elif "do " in line_lower or "dos" in line_lower:
        return IssueType.DOS_VIOLATION
    elif "don't" in line_lower or "dont" in line_lower or "donts" in line_lower:
        return IssueType.DONTS_VIOLATION
    elif "style" in line_lower or "format" in line_lower:
        return IssueType.STYLE_INCONSISTENCY
    else:
        return IssueType.GENERAL


def collect_evidence(state: Dict[str, Any]) -> Dict[str, Any]:
    """Collect evidence for issues identified in content."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        brand_voice = state["brand_voice"]
        content = state["content"]
        issues = state.get("issues", [])
        
        # Skip if no issues found
        if not issues:
            state["evidence"] = {}
            state["analysis_stage"] = "evidence_collected"
            return state
        
        # Create system prompt
        system_prompt = EVIDENCE_COLLECTOR_PROMPT.format(
            personality=brand_voice.get("voice_metadata", {}).get("personality", "Not specified"),
            tonality=brand_voice.get("voice_metadata", {}).get("tonality", "Not specified"),
            dos=brand_voice.get("dos", "Not specified"),
            donts=brand_voice.get("donts", "Not specified")
        )
        
        # Prepare issues for the prompt
        issues_text = ""
        for i, issue in enumerate(issues):
            issues_text += f"{i+1}. {issue['text']}\n   Type: {issue['issue_type']}\n   Explanation: {issue['explanation']}\n\n"
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Content: {content}\n\nIssues identified:\n{issues_text}\n\nPlease collect evidence for each issue.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Extract evidence from response
        evidence = extract_evidence(response.content, issues, content)
        
        # Update state
        state["evidence"] = evidence
        state["analysis_stage"] = "evidence_collected"
        
        # Update issues with positions and severity
        for issue in issues:
            issue_id = issue["id"]
            if issue_id in evidence:
                # Find position of the first evidence text in content
                evidence_text = evidence[issue_id][0] if evidence[issue_id] else ""
                if evidence_text:
                    start_index, end_index = find_text_position(content, evidence_text)
                    issue["start_index"] = start_index
                    issue["end_index"] = end_index
                
                # Calculate severity based on evidence
                issue["severity"] = calculate_severity(evidence[issue_id])
        
        # Add messages to state for debugging/logging
        state["messages"] = state.get("messages", []) + [{
            "role": "system",
            "content": f"Evidence collected for {len(evidence)} issues."
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


def extract_evidence(response_text: str, issues: List[Dict[str, Any]], content: str) -> Dict[str, List[str]]:
    """Extract evidence from LLM response."""
    evidence = {}
    
    # Initialize evidence for each issue
    for issue in issues:
        evidence[issue["id"]] = []
    
    # Simple parsing logic
    lines = response_text.split("\n")
    current_issue_idx = -1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for issue markers (numbered items)
        if line.startswith(tuple(f"{i+1}." for i in range(len(issues)))):
            try:
                # Extract issue number
                current_issue_idx = int(line.split(".", 1)[0]) - 1
            except:
                continue
        elif line.lower().startswith("evidence:") and 0 <= current_issue_idx < len(issues):
            # Add evidence to current issue
            evidence_text = line.split(":", 1)[1].strip() if ":" in line else line
            if evidence_text and current_issue_idx < len(issues):
                evidence[issues[current_issue_idx]["id"]].append(evidence_text)
        elif line.startswith("-") and 0 <= current_issue_idx < len(issues):
            # Add bullet point evidence
            evidence_text = line[1:].strip()
            if evidence_text and current_issue_idx < len(issues):
                evidence[issues[current_issue_idx]["id"]].append(evidence_text)
    
    return evidence


def find_text_position(content: str, text: str) -> Tuple[int, int]:
    """Find the position of text in content."""
    start = content.find(text)
    if start >= 0:
        return start, start + len(text)
    return 0, 0


def calculate_severity(evidence: List[str]) -> float:
    """Calculate severity based on evidence."""
    # Simple severity calculation
    if not evidence:
        return 0.5  # Default medium severity
    
    # Count strong negative words in evidence
    strong_words = ["completely", "severely", "extremely", "totally", "very", "significant", "major"]
    medium_words = ["somewhat", "partially", "slightly", "minor", "a bit"]
    
    strong_count = 0
    medium_count = 0
    
    for item in evidence:
        item_lower = item.lower()
        for word in strong_words:
            if word in item_lower:
                strong_count += 1
        for word in medium_words:
            if word in item_lower:
                medium_count += 1
    
    # Calculate severity score (0.0 to 1.0)
    base_severity = 0.5
    strong_factor = 0.1 * strong_count
    medium_factor = 0.05 * medium_count
    
    severity = base_severity + strong_factor - medium_factor
    
    # Clamp to valid range
    return max(0.1, min(0.9, severity))


def calculate_scores(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate scores based on content analysis and evidence."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
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
        
        # Prepare issues and evidence for the prompt
        analysis_text = ""
        for i, issue in enumerate(issues):
            issue_id = issue["id"]
            issue_evidence = evidence.get(issue_id, [])
            
            analysis_text += f"{i+1}. {issue['text']}\n"
            analysis_text += f"   Type: {issue['issue_type']}\n"
            analysis_text += f"   Severity: {issue['severity']}\n"
            analysis_text += f"   Explanation: {issue['explanation']}\n"
            
            if issue_evidence:
                analysis_text += "   Evidence:\n"
                for j, ev in enumerate(issue_evidence):
                    analysis_text += f"   - {ev}\n"
            
            analysis_text += "\n"
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Content length: {len(content)} characters\nNumber of issues: {len(issues)}\n\nAnalysis:\n{analysis_text}\n\nPlease calculate scores for this content.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Parse scores from response
        scores = parse_scores(response.content)
        
        # Update state
        state["scores"] = scores
        state["analysis_stage"] = "scores_calculated"
        
        # Add messages to state for debugging/logging
        state["messages"] = state.get("messages", []) + [{
            "role": "system",
            "content": f"Scores calculated. Overall score: {scores.get('overall', 0.5)}"
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


def parse_scores(response_text: str) -> Dict[str, float]:
    """Parse scores from LLM response."""
    scores = {
        "overall": 0.5,      # Default scores
        "personality": 0.5,
        "tonality": 0.5,
        "dos": 0.5,
        "donts": 0.5
    }
    
    # Simple parsing logic
    lines = response_text.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for score patterns like "Overall Score: 0.8" or "Personality: 0.7"
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip().lower()
            
            # Try to extract a score (0.0 to 1.0)
            try:
                value_part = parts[1].strip()
                # Extract the first number found
                import re
                numbers = re.findall(r"0\.\d+|\d+\.\d+|\d+", value_part)
                if numbers:
                    value = float(numbers[0])
                    # Normalize to 0.0-1.0 range if needed
                    if value > 1.0 and value <= 10.0:
                        value = value / 10.0
                    elif value > 10.0 and value <= 100.0:
                        value = value / 100.0
                    
                    # Clamp to valid range
                    value = max(0.0, min(1.0, value))
                    
                    # Map to our score keys
                    if "overall" in key:
                        scores["overall"] = value
                    elif "personality" in key:
                        scores["personality"] = value
                    elif "tone" in key or "tonality" in key:
                        scores["tonality"] = value
                    elif "do" in key and "s" in key:  # Match "dos" but not "don'ts"
                        scores["dos"] = value
                    elif "don" in key:  # Match "don'ts", "donts", etc.
                        scores["donts"] = value
            except:
                continue
    
    return scores


def generate_suggestions(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate suggestions for improving content alignment with brand voice."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        brand_voice = state["brand_voice"]
        content = state["content"]
        issues = state.get("issues", [])
        options = state.get("options", {})
        
        # Skip if no issues or suggestions not requested
        if not issues or not options.get("include_suggestions", True):
            state["suggestions"] = []
            state["analysis_stage"] = "suggestions_generated"
            return state
        
        # Limit number of issues to process based on options
        max_suggestions = options.get("max_suggestions", 5)
        issues_to_process = sorted(issues, key=lambda x: x.get("severity", 0.5), reverse=True)[:max_suggestions]
        
        # Create system prompt
        system_prompt = SUGGESTION_GENERATOR_PROMPT.format(
            personality=brand_voice.get("voice_metadata", {}).get("personality", "Not specified"),
            tonality=brand_voice.get("voice_metadata", {}).get("tonality", "Not specified"),
            dos=brand_voice.get("dos", "Not specified"),
            donts=brand_voice.get("donts", "Not specified")
        )
        
        # Prepare issues for the prompt
        issues_text = ""
        for i, issue in enumerate(issues_to_process):
            issues_text += f"{i+1}. {issue['text']}\n"
            issues_text += f"   Type: {issue['issue_type']}\n"
            issues_text += f"   Severity: {issue['severity']}\n"
            issues_text += f"   Explanation: {issue['explanation']}\n\n"
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Content: {content}\n\nIssues to address:\n{issues_text}\n\nPlease generate suggestions to improve this content.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Parse suggestions from response
        suggestions = parse_suggestions(response.content, issues_to_process)
        
        # Update state
        state["suggestions"] = suggestions
        state["analysis_stage"] = "suggestions_generated"
        
        # Add messages to state for debugging/logging
        state["messages"] = state.get("messages", []) + [{
            "role": "system",
            "content": f"Generated {len(suggestions)} suggestions."
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


def parse_suggestions(response_text: str, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse suggestions from LLM response."""
    suggestions = []
    
    # Simple parsing logic
    lines = response_text.split("\n")
    current_suggestion = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for suggestion markers (numbered items or "Suggestion:")
        if line.startswith(tuple(f"{i+1}." for i in range(10))) or line.lower().startswith("suggestion:"):
            # Save previous suggestion if exists
            if current_suggestion and "original_text" in current_suggestion and "suggested_text" in current_suggestion:
                suggestions.append(current_suggestion)
            
            # Start new suggestion
            current_suggestion = {
                "id": str(uuid.uuid4()),
                "original_text": "",
                "suggested_text": "",
                "explanation": "",
                "category": SuggestionCategory.GENERAL,
                "priority": 2  # Default medium priority
            }
            
            # Extract suggestion title
            if ":" in line:
                title = line.split(":", 1)[1].strip()
                if title:
                    current_suggestion["explanation"] = title
        elif current_suggestion and line.lower().startswith("original:"):
            # Extract original text
            current_suggestion["original_text"] = line.split(":", 1)[1].strip() if ":" in line else ""
        elif current_suggestion and line.lower().startswith(("suggested:", "replacement:", "new:")):
            # Extract suggested text
            current_suggestion["suggested_text"] = line.split(":", 1)[1].strip() if ":" in line else ""
        elif current_suggestion and line.lower().startswith("explanation:"):
            # Extract explanation
            current_suggestion["explanation"] = line.split(":", 1)[1].strip() if ":" in line else ""
        elif current_suggestion and line.lower().startswith("category:"):
            # Extract category
            category_text = line.split(":", 1)[1].strip().lower() if ":" in line else ""
            if "personality" in category_text:
                current_suggestion["category"] = SuggestionCategory.PERSONALITY
            elif "tone" in category_text or "tonality" in category_text:
                current_suggestion["category"] = SuggestionCategory.TONALITY
            elif "do" in category_text and "s" in category_text and "n't" not in category_text:
                current_suggestion["category"] = SuggestionCategory.DOS
            elif "don't" in category_text or "dont" in category_text:
                current_suggestion["category"] = SuggestionCategory.DONTS
            elif "style" in category_text:
                current_suggestion["category"] = SuggestionCategory.STYLE
        elif current_suggestion and line.lower().startswith("priority:"):
            # Extract priority
            priority_text = line.split(":", 1)[1].strip().lower() if ":" in line else ""
            if "high" in priority_text or "1" in priority_text:
                current_suggestion["priority"] = 1
            elif "medium" in priority_text or "2" in priority_text:
                current_suggestion["priority"] = 2
            elif "low" in priority_text or "3" in priority_text:
                current_suggestion["priority"] = 3
        elif current_suggestion and not current_suggestion["explanation"]:
            # If no specific marker and no explanation yet, use this line as explanation
            current_suggestion["explanation"] = line
    
    # Add the last suggestion if exists
    if current_suggestion and "original_text" in current_suggestion and "suggested_text" in current_suggestion:
        suggestions.append(current_suggestion)
    
    # Link suggestions to issues if possible
    for suggestion in suggestions:
        for issue in issues:
            # Simple heuristic: if the original text in suggestion appears in the issue text
            if suggestion["original_text"] and suggestion["original_text"] in issue["text"]:
                suggestion["issue_id"] = issue["id"]
                break
    
    return suggestions


def generate_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the final analysis report."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        brand_voice = state["brand_voice"]
        content = state["content"]
        issues = state.get("issues", [])
        suggestions = state.get("suggestions", [])
        scores = state.get("scores", {})
        options = state.get("options", {})
        
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
        if options.get("generate_report", True):
            report = generate_text_report(
                llm=llm,
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


def generate_text_report(llm, content: str, brand_voice: Dict[str, Any], 
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
    response = llm.invoke(messages)
    
    return response.content

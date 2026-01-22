import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini client
# Note: Using the synchronous client for simplicity as per original design, 
# but in a real high-scale app, async client would be better.
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def fallback_json(error_msg: str = "Invalid LLM output") -> dict:
    """Return a safe fallback JSON object if parsing fails."""
    return {
        "summary": error_msg,
        "type": "other",
        "priority_score": "1 - Unable to determine priority due to error",
        "suggested_labels": [],
        "potential_impact": "LLM failed to return valid JSON"
    }

def extract_json(text: str) -> dict:
    """Extract valid JSON from LLM response text."""
    start = text.find("{")
    end = text.rfind("}")
    
    if start == -1 or end == -1 or start > end:
        return fallback_json("No JSON found in response")
        
    try:
        return json.loads(text[start:end+1])
    except json.JSONDecodeError:
        return fallback_json("JSON parse error")

def sanitize_output(data: dict) -> dict:
    """Ensure output conforms to the expected schema and types."""
    # Ensure suggested_labels is a list of strings
    labels = data.get("suggested_labels", [])
    if isinstance(labels, dict):
        labels = list(labels.values())
    if not isinstance(labels, list):
        labels = []
    
    # Clean labels and priority
    data["suggested_labels"] = [str(l).strip() for l in labels if l][:3]
    data["priority_score"] = str(data.get("priority_score", "1 - Default score"))

    # Fill missing keys with defaults
    required = {
        "summary": "No summary provided",
        "type": "other",
        "priority_score": "1 - Default score",
        "suggested_labels": [],
        "potential_impact": "Unknown"
    }
    
    for key, default in required.items():
        if key not in data:
            data[key] = default
            
    return data

def analyze_with_gemini(issue_text: str) -> dict:
    """
    Analyze a GitHub issue using Google Gemini with few-shot prompting.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        return fallback_json("Server Error: Google API Key not configured")

    # Few-Shot Prompting: Providing examples improves reliability
    system_instruction = """
You are an expert GitHub Issue Triage AI. Your job is to analyze issue descriptions and output a STRICT JSON classification.

Output Schema:
{
  "summary": "1-2 sentence summary of the issue",
  "type": "bug | feature_request | documentation | question | other",
  "priority_score": "A score from 1 (low) to 5 (critical), with a brief justification for the score.",
  "suggested_labels": ["label1", "label2", "label3"],
  "potential_impact": "Brief description of the impact on users or codebase"
}

IMPORTANT: valid "suggested_labels" count is maximum 3.

---
Example 1:
Input:
Title: Login page crashes on iOS 15
Body: When I try to login on my iPhone running iOS 15, the app immediately closes.
Comments: Me too!

Output:
{
  "summary": "The application crashes immediately upon login attempts on iOS 15 devices.",
  "type": "bug",
  "priority_score": "5 - Critical blocker that prevents users from accessing the application",
  "suggested_labels": ["ios", "crash", "bug"],
  "potential_impact": "Complete blocker for all iOS 15 users."
}

Example 2:
Input:
Title: Add Dark Mode support
Body: It would be great if we could have a dark mode for night time usage.

Output:
{
  "summary": "Request to implement a dark mode theme for better low-light usability.",
  "type": "feature_request",
  "priority_score": "2 - Nice to have feature but not critical for functionality",
  "suggested_labels": ["enhancement", "ui/ux", "good-first-issue"],
  "potential_impact": "Improves user experience and accessibility, but not critical for functionality."
}
---
"""

    prompt = f"""
Analyze the following GitHub Issue:

{issue_text}

OUTPUT ONLY THE JSON OBJECT.
"""
    
    try:
        # Generate content
        response = client.models.generate_content(
            model="models/gemini-flash-lite-latest", # Using 1.5 Flash for speed/cost efficiency
            contents=[system_instruction, prompt]
        )
        
        parsed = extract_json(response.text)
        return sanitize_output(parsed)
        
    except Exception as e:
        return fallback_json(f"Gemini API Error: {str(e)}")

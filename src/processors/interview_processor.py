"""Process customer interview documents."""

import re
from typing import Dict, Any, List

from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class InterviewProcessor:
    """
    Process customer interview data to extract insights.

    Uses Claude to analyze interview text and extract:
    - Key pain points
    - Feature requests
    - Customer sentiment
    - Quotes and evidence
    """

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=config.anthropic_api_key,
            temperature=0.3,
        )

    def process_interview(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a customer interview document.

        Args:
            document_data: Parsed document data

        Returns:
            Processed interview insights
        """
        if "error" in document_data:
            return {
                "file_name": document_data.get("file_name"),
                "error": document_data["error"]
            }

        text = document_data.get("text", "")
        if not text:
            return {
                "file_name": document_data.get("file_name"),
                "error": "No text content found"
            }

        logger.info(f"Processing interview: {document_data.get('file_name')}")

        # Extract insights using Claude
        insights = self._extract_insights(text)

        return {
            "file_name": document_data.get("file_name"),
            "file_type": document_data.get("file_type"),
            "insights": insights,
            "raw_text": text[:500] + "..." if len(text) > 500 else text,  # Preview
        }

    def _extract_insights(self, text: str) -> Dict[str, Any]:
        """
        Extract insights from interview text using Claude.

        Args:
            text: Interview text

        Returns:
            Extracted insights
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert product manager analyzing customer interviews.
Extract the following from the interview:
1. Pain points (specific problems customers face)
2. Feature requests (what they want to see)
3. Positive feedback (what they like)
4. Overall sentiment (positive, neutral, negative)
5. Key quotes (exact quotes that are insightful)

Format your response as JSON with these exact keys:
{
  "pain_points": ["point 1", "point 2", ...],
  "feature_requests": ["request 1", "request 2", ...],
  "positive_feedback": ["feedback 1", "feedback 2", ...],
  "sentiment": "positive/neutral/negative",
  "key_quotes": ["quote 1", "quote 2", ...],
  "summary": "Brief 2-3 sentence summary"
}"""),
            ("user", "Interview text:\n\n{text}")
        ])

        try:
            chain = prompt | self.llm
            response = chain.invoke({"text": text})

            # Parse JSON from response
            import json
            content = response.content

            # Extract JSON from markdown code block if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            insights = json.loads(content)
            logger.info("Successfully extracted insights from interview")
            return insights

        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return {
                "pain_points": [],
                "feature_requests": [],
                "positive_feedback": [],
                "sentiment": "unknown",
                "key_quotes": [],
                "summary": "Error processing interview",
                "error": str(e)
            }

    def aggregate_interviews(self, interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate insights from multiple interviews.

        Args:
            interviews: List of processed interview data

        Returns:
            Aggregated insights
        """
        all_pain_points = []
        all_feature_requests = []
        all_positive_feedback = []
        all_quotes = []
        sentiments = []

        for interview in interviews:
            insights = interview.get("insights", {})
            all_pain_points.extend(insights.get("pain_points", []))
            all_feature_requests.extend(insights.get("feature_requests", []))
            all_positive_feedback.extend(insights.get("positive_feedback", []))
            all_quotes.extend(insights.get("key_quotes", []))
            if insights.get("sentiment"):
                sentiments.append(insights["sentiment"])

        # Calculate overall sentiment
        sentiment_scores = {
            "positive": sentiments.count("positive"),
            "neutral": sentiments.count("neutral"),
            "negative": sentiments.count("negative"),
        }
        overall_sentiment = max(sentiment_scores, key=sentiment_scores.get)

        return {
            "total_interviews": len(interviews),
            "pain_points": all_pain_points,
            "feature_requests": all_feature_requests,
            "positive_feedback": all_positive_feedback,
            "key_quotes": all_quotes[:20],  # Top 20 quotes
            "overall_sentiment": overall_sentiment,
            "sentiment_distribution": sentiment_scores,
        }

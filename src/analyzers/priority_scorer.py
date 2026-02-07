"""Score and prioritize features using various frameworks."""

from typing import Dict, Any, List

from ..utils.logger import get_logger

logger = get_logger(__name__)


class PriorityScorer:
    """
    Score and prioritize features using product management frameworks.

    Supports multiple scoring methodologies:
    - RICE (Reach, Impact, Confidence, Effort)
    - ICE (Impact, Confidence, Ease)
    - Value vs. Effort
    """

    @staticmethod
    def rice_score(
        reach: int,
        impact: float,
        confidence: float,
        effort: float
    ) -> float:
        """
        Calculate RICE score.

        Args:
            reach: Number of users affected per period
            impact: Impact score (0.25, 0.5, 1, 2, 3)
            confidence: Confidence level (0-100%)
            effort: Effort in person-months

        Returns:
            RICE score
        """
        if effort == 0:
            return 0
        return (reach * impact * confidence) / effort

    @staticmethod
    def ice_score(impact: float, confidence: float, ease: float) -> float:
        """
        Calculate ICE score.

        Args:
            impact: Impact score (1-10)
            confidence: Confidence score (1-10)
            ease: Ease score (1-10)

        Returns:
            ICE score
        """
        return impact * confidence * ease

    @staticmethod
    def score_feature(
        feature: Dict[str, Any],
        method: str = "rice"
    ) -> Dict[str, Any]:
        """
        Score a single feature.

        Args:
            feature: Feature data
            method: Scoring method (rice, ice, value_effort)

        Returns:
            Feature with score added
        """
        scored_feature = feature.copy()

        if method == "rice":
            # Estimate RICE parameters from feature data
            reach = PriorityScorer._estimate_reach(feature)
            impact = PriorityScorer._estimate_impact(feature)
            confidence_pct = PriorityScorer._parse_confidence(feature)
            effort = PriorityScorer._estimate_effort(feature)

            score = PriorityScorer.rice_score(reach, impact, confidence_pct, effort)
            scored_feature["rice_score"] = round(score, 2)
            scored_feature["rice_components"] = {
                "reach": reach,
                "impact": impact,
                "confidence": confidence_pct,
                "effort": effort,
            }

        elif method == "ice":
            impact = PriorityScorer._estimate_impact(feature) * 3.33  # Scale to 10
            confidence = PriorityScorer._parse_confidence(feature) * 10  # Scale to 10
            ease = 10 - min(PriorityScorer._estimate_effort(feature) * 2, 10)  # Inverse of effort

            score = PriorityScorer.ice_score(impact, confidence, ease)
            scored_feature["ice_score"] = round(score, 2)
            scored_feature["ice_components"] = {
                "impact": round(impact, 1),
                "confidence": round(confidence, 1),
                "ease": round(ease, 1),
            }

        return scored_feature

    @staticmethod
    def _estimate_reach(feature: Dict[str, Any]) -> int:
        """Estimate reach based on feature data."""
        # Use evidence count as proxy
        evidence_count = len(feature.get("evidence", []))
        # More evidence = more users affected
        return max(evidence_count * 500, 100)  # Scale up

    @staticmethod
    def _estimate_impact(feature: Dict[str, Any]) -> float:
        """Estimate impact (0.25 to 3.0 scale for RICE)."""
        confidence = feature.get("confidence", "medium")
        impact_map = {
            "high": 2.0,
            "medium": 1.0,
            "low": 0.5,
        }
        return impact_map.get(confidence, 1.0)

    @staticmethod
    def _parse_confidence(feature: Dict[str, Any]) -> float:
        """Parse confidence to 0-1 scale."""
        confidence = feature.get("confidence", "medium")
        confidence_map = {
            "high": 0.9,
            "medium": 0.6,
            "low": 0.3,
        }
        return confidence_map.get(confidence, 0.6)

    @staticmethod
    def _estimate_effort(feature: Dict[str, Any]) -> float:
        """Estimate effort in person-months."""
        # Use description length as rough proxy
        description = feature.get("description", "")
        # More complex descriptions = more effort
        if len(description) > 200:
            return 3.0
        elif len(description) > 100:
            return 2.0
        else:
            return 1.0

    @classmethod
    def score_all(
        cls,
        features: List[Dict[str, Any]],
        method: str = "rice"
    ) -> List[Dict[str, Any]]:
        """
        Score all features and return sorted by priority.

        Args:
            features: List of features
            method: Scoring method

        Returns:
            Scored and sorted features
        """
        scored_features = [cls.score_feature(f, method) for f in features]

        # Sort by score
        score_key = f"{method}_score"
        scored_features.sort(key=lambda x: x.get(score_key, 0), reverse=True)

        logger.info(f"Scored {len(scored_features)} features using {method.upper()}")
        return scored_features

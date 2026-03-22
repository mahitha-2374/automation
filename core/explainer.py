"""
Explainability Engine
Explains why columns are mapped to specific categories
"""


class Explainer:
    """Provide human-readable explanations for mappings"""

    def explain_column(self, column, category, score, source):
        """
        Create explanation for why a column was mapped
        
        Args:
            column: Column name
            category: Mapped category
            score: Confidence score
            source: Source of mapping (rule, semantic, learned)
            
        Returns:
            dict: Explanation object
        """
        source_descriptions = {
            "rule": "Rule-based pattern matching",
            "semantic": "Semantic similarity analysis",
            "learned": "Retrieved from learning memory"
        }

        return {
            "column": column,
            "mapped_as": category,
            "confidence": round(float(score), 3),
            "source": source,
            "source_description": source_descriptions.get(source, "Unknown"),
            "reason": f"{column} was interpreted as {category} using {source_descriptions.get(source, 'unknown')} (confidence: {round(float(score), 3)})"
        }

    def get_explanation_report(self, explanations):
        """Create a structured report from explanations"""
        return {
            "total_mappings": len(explanations),
            "high_confidence": sum(1 for e in explanations if e["confidence"] >= 0.7),
            "medium_confidence": sum(1 for e in explanations if 0.5 <= e["confidence"] < 0.7),
            "low_confidence": sum(1 for e in explanations if e["confidence"] < 0.5),
            "details": explanations
        }

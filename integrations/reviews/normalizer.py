from typing import Dict, Any
from .models.review import AppReviewModel

class ReviewsNormalizer:
    
    @staticmethod
    def normalize_review(review: AppReviewModel) -> Dict[str, Any]:
        """Converts an App Review into an AgentOS UniversalEvent."""
        
        severity = "Critical" if review.is_critical_regression else "High" if review.rating <= 2 else "Low"

        return {
            "source": f"reviews_{review.provider}",
            "entity_type": "review",
            "repository": f"App_{review.app_id}",
            "title": f"{review.rating}⭐ Review [v{review.version}]: {review.title}",
            "description": review.body,
            "author": "Public_User",
            "severity": severity,
            "timestamp": review.created_at.isoformat(),
            "metadata": {
                "review_id": review.id,
                "rating": review.rating,
                "app_version": review.version,
                "country": review.country
            },
            # Correlate this version string with GitHub releases and Datadog/Sentry crashes!
            "linked_entities": [] 
        }
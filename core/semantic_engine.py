"""
Semantic Intelligence Layer
Understands IAM concepts independent of column naming
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SemanticEngine:
    """Uses semantic similarity to understand column meaning"""

    def __init__(self):
        """Initialize semantic engine with pre-trained model"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            print("Downloading semantic model (first time only)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Semantic concepts for IAM
        self.concepts = {
            "user": ["user id", "login id", "account name", "employee", "user name", "userid"],
            "role": ["role", "group", "access bundle", "profile", "access group", "role name"],
            "entitlement": ["permission", "access right", "privilege", "capability", "resource", "entitlement"],
            "module": ["application", "system", "platform", "service", "module", "application name"],
            "subcategory": ["feature", "function", "sub module", "submodule", "category"]
        }

        # Pre-encode concept vectors for efficiency
        self.concept_embeddings = {}
        for key, vals in self.concepts.items():
            self.concept_embeddings[key] = self.model.encode(vals)

    def get_best_match(self, column_name):
        """
        Find best semantic match for a column name
        
        Args:
            column_name: The column name to classify
            
        Returns:
            tuple: (category, confidence_score)
        """
        col_vec = self.model.encode([column_name])
        best_category = None
        best_score = 0

        for concept, embeddings in self.concept_embeddings.items():
            scores = cosine_similarity(col_vec, embeddings)
            score = np.max(scores)

            if score > best_score:
                best_score = score
                best_category = concept

        return best_category, float(best_score)

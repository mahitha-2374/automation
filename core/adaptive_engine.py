"""
Main Adaptive Engine
Combines semantic understanding, learning, and explainability
"""

import pandas as pd
from core.semantic_engine import SemanticEngine
from core.learning_engine import LearningEngine
from core.explainer import Explainer


class AdaptiveEngine:
    """
    Main intelligence engine that adapts to any IAM data schema
    """

    def __init__(self):
        """Initialize the adaptive engine with all components"""
        self.semantic = SemanticEngine()
        self.memory = LearningEngine()
        self.explainer = Explainer()

    def detect_schema(self, df):
        """
        Intelligently detect schema from dataframe
        
        Strategy:
        1. Check memory (learned mappings)
        2. Use semantic matching
        3. Store result for future learning
        
        Args:
            df: Input dataframe
            
        Returns:
            tuple: (mapping dict, explanations list)
        """
        mapping = {}
        explanations = []

        for col in df.columns:
            learned = self.memory.get(col)

            if learned:
                # Use learned mapping
                mapping[learned["category"]] = col
                explanations.append(
                    self.explainer.explain_column(
                        col,
                        learned["category"],
                        learned["confidence"],
                        "learned"
                    )
                )
            else:
                # Use semantic detection
                category, score = self.semantic.get_best_match(col)

                if category:
                    mapping[category] = col
                    self.memory.store(col, category, score)

                    explanations.append(
                        self.explainer.explain_column(
                            col, category, score, "semantic"
                        )
                    )

        return mapping, explanations

    def build_entitlement(self, row, schema):
        """
        Dynamically build entitlement hierarchy
        
        Handles various combinations:
        - module > category > subcategory > entitlement
        - module > entitlement
        - any combination that exists
        
        Args:
            row: Data row
            schema: Column mapping
            
        Returns:
            str: Formatted entitlement hierarchy
        """
        parts = []

        # Build hierarchy dynamically
        for key in ["module", "subcategory", "entitlement"]:
            col = schema.get(key)
            if col and pd.notna(row.get(col)):
                val = str(row[col]).strip()
                if val and val.lower() != "nan":
                    parts.append(val)

        return " > ".join(parts) if parts else "UNKNOWN"

    def generate_description(self, entitlement, role):
        """Generate descriptive text for entitlement + role combo"""
        return f"{role} can perform actions on {entitlement}"

    def process(self, user_df, role_df, gsi_id=None):
        """
        Main processing pipeline
        
        Args:
            user_df: User export data
            role_df: Role export data
            gsi_id: GlobalSystemID of the application (optional)
            
        Returns:
            dict: Fully structured IAM data
        """
        # Detect schemas
        user_schema, user_explain = self.detect_schema(user_df)
        role_schema, role_explain = self.detect_schema(role_df)

        user_map = {}
        role_map = {}

        # Build user → role mapping
        if user_schema.get("user") and user_schema.get("role"):
            for _, row in user_df.iterrows():
                user = row.get(user_schema["user"])
                role = row.get(user_schema["role"])

                if pd.notna(user):
                    user_str = str(user).strip()
                    if user_str not in user_map:
                        user_map[user_str] = []

                    if pd.notna(role):
                        role_str = str(role).strip()
                        if role_str and role_str not in user_map[user_str]:
                            user_map[user_str].append(role_str)

        # Build role → entitlement mapping
        if role_schema.get("role"):
            for _, row in role_df.iterrows():
                role = row.get(role_schema.get("role"))

                if pd.notna(role):
                    role_str = str(role).strip()
                    ent = self.build_entitlement(row, role_schema)

                    if role_str not in role_map:
                        role_map[role_str] = []

                    if ent not in role_map[role_str]:
                        role_map[role_str].append(ent)

        # Build final structure
        data = {
            "gsi_id": gsi_id or "NOT_PROVIDED",
            "users": [],
            "roles": [],
            "entitlements": [],
            "explanations": user_explain + role_explain,
            "schema_info": {
                "user_schema": user_schema,
                "role_schema": role_schema
            }
        }

        # Populate users
        for user, roles in user_map.items():
            data["users"].append({
                "user_id": user,
                "roles": roles,
                "account_status": "ACTIVE"
            })

        # Populate roles and entitlements
        for role, entitlements in role_map.items():
            data["roles"].append({
                "role_name": role,
                "entitlements": entitlements
            })

            for ent in entitlements:
                # Check if entitlement already exists
                existing = [e for e in data["entitlements"] if e["resource_name"] == ent]
                if not existing:
                    data["entitlements"].append({
                        "resource_name": ent,
                        "description": self.generate_description(ent, role)
                    })

        return data

"""
Explainability Report Generator
Creates audit-ready reports from mapping explanations
"""

import pandas as pd


class ExplainReport:
    """Generate explainability and audit reports"""

    def generate(self, explanations, output_path):
        """
        Generate Excel report from explanations
        
        Args:
            explanations: List of explanation dicts
            output_path: Where to save the report
        """
        df = pd.DataFrame(explanations)

        # Sort by confidence (lowest first - for audit focus)
        df = df.sort_values("confidence")

        # Write to Excel
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Mappings", index=False)

            # Add summary sheet
            summary = self._create_summary(df)
            summary.to_excel(writer, sheet_name="Summary", index=False)

    def _create_summary(self, df):
        """Create summary statistics"""
        total = len(df)
        high_conf = len(df[df["confidence"] >= 0.7])
        medium_conf = len(df[(df["confidence"] >= 0.5) & (df["confidence"] < 0.7)])
        low_conf = len(df[df["confidence"] < 0.5])

        summary_data = {
            "Metric": [
                "Total Mappings",
                "High Confidence (≥0.7)",
                "Medium Confidence (0.5-0.7)",
                "Low Confidence (<0.5)",
                "Average Confidence"
            ],
            "Value": [
                total,
                high_conf,
                medium_conf,
                low_conf,
                round(df["confidence"].mean(), 3)
            ]
        }

        return pd.DataFrame(summary_data)

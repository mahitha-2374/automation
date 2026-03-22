"""
Configuration
"""

import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Create directories if they don't exist
for directory in [INPUT_DIR, OUTPUT_DIR, TEMPLATE_DIR, MEMORY_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Template paths
TEMPLATE_PATHS = {
    "excel": os.path.join(TEMPLATE_DIR, "T3_template.xlsm"),
    "word": os.path.join(TEMPLATE_DIR, "OLA_template.docx")
}

# Output paths
OUTPUT_PATHS = {
    "excel": os.path.join(OUTPUT_DIR, f"T3_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsm"),
    "word": os.path.join(OUTPUT_DIR, f"OLA_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"),
    "report": os.path.join(OUTPUT_DIR, f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
}

# Semantic model
SEMANTIC_MODEL = "all-MiniLM-L6-v2"

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.7,
    "medium": 0.5,
    "low": 0.0
}

# Logging
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

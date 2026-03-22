"""
Flask REST API
For programmatic integration
"""

from flask import Flask, request, jsonify
import pandas as pd
import os
from io import StringIO
import traceback

from core.adaptive_engine import AdaptiveEngine
from generators.excel_generator import ExcelGenerator
from generators.word_generator import WordGenerator
from generators.report_generator import ExplainReport


def load_input_dataframe(uploaded_file):
    """Load CSV or Excel uploads into a DataFrame."""
    file_name = (uploaded_file.filename or "").lower()
    uploaded_file.stream.seek(0)
    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file.stream)
    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file.stream, engine="openpyxl")
    raise ValueError("Unsupported file type. Please upload CSV, XLSX, or XLS files.")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "IAM Automation Platform",
        "version": "1.0"
    }), 200

@app.route('/process', methods=['POST'])
def process():
    """
    Main processing endpoint
    
    Expects:
    - user_file: CSV/XLSX/XLS file (multipart)
    - role_file: CSV/XLSX/XLS file (multipart)
    - gsi_id: Global System ID (optional)
    
    Returns:
    - Processed IAM data as JSON
    """
    try:
        if 'user_file' not in request.files or 'role_file' not in request.files:
            return jsonify({"error": "Missing files"}), 400

        user_file = request.files['user_file']
        role_file = request.files['role_file']
        gsi_id = request.form.get('gsi_id', None)

        # Read files
        user_df = load_input_dataframe(user_file)
        role_df = load_input_dataframe(role_file)

        # Process
        engine = AdaptiveEngine()
        result = engine.process(user_df, role_df, gsi_id=gsi_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/process/excel', methods=['POST'])
def process_and_generate_excel():
    """Process and generate T3 Excel"""
    try:
        if 'user_file' not in request.files or 'role_file' not in request.files:
            return jsonify({"error": "Missing files"}), 400

        user_file = request.files['user_file']
        role_file = request.files['role_file']

        user_df = load_input_dataframe(user_file)
        role_df = load_input_dataframe(role_file)

        engine = AdaptiveEngine()
        result = engine.process(user_df, role_df)

        os.makedirs("output", exist_ok=True)
        output_path = "output/T3_api_output.xlsm"

        ExcelGenerator().generate("templates/T3_template.xlsm", output_path, result)

        with open(output_path, 'rb') as f:
            excel_content = f.read()

        return excel_content, 200, {
            'Content-Disposition': 'attachment; filename=T3_output.xlsm',
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process/word', methods=['POST'])
def process_and_generate_word():
    """Process and generate OLA Word"""
    try:
        if 'user_file' not in request.files or 'role_file' not in request.files:
            return jsonify({"error": "Missing files"}), 400

        user_file = request.files['user_file']
        role_file = request.files['role_file']

        user_df = load_input_dataframe(user_file)
        role_df = load_input_dataframe(role_file)

        engine = AdaptiveEngine()
        result = engine.process(user_df, role_df)

        os.makedirs("output", exist_ok=True)
        output_path = "output/OLA_api_output.docx"

        WordGenerator().generate("templates/OLA_template.docx", output_path, result)

        with open(output_path, 'rb') as f:
            word_content = f.read()

        return word_content, 200, {
            'Content-Disposition': 'attachment; filename=OLA_output.docx',
            'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/schema/detect', methods=['POST'])
def detect_schema():
    """
    Detect schema from a file
    Returns column mappings and confidence scores
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        df = load_input_dataframe(file)

        engine = AdaptiveEngine()
        mapping, explanations = engine.detect_schema(df)

        return jsonify({
            "mapping": mapping,
            "explanations": explanations
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/learning/memory', methods=['GET'])
def get_learning_memory():
    """Get current learning memory"""
    try:
        from core.learning_engine import LearningEngine
        memory = LearningEngine()
        return jsonify(memory.get_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/learning/memory', methods=['DELETE'])
def clear_learning_memory():
    """Clear learning memory"""
    try:
        from core.learning_engine import LearningEngine
        memory = LearningEngine()
        memory.clear()
        return jsonify({"status": "Memory cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

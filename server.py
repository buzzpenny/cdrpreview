import os
import subprocess
import uuid
import logging
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS so your HTML file can talk to this server from anywhere
CORS(app)

# Configure paths
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "cdr-converter"}), 200

@app.route('/convert', methods=['POST'])
def convert_cdr():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Generate unique filenames
    unique_id = str(uuid.uuid4())
    # Sanitize extension or force it
    input_filename = f"{unique_id}.cdr" 
    output_filename = f"{unique_id}.png"
    
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    try:
        file.save(input_path)
        logger.info(f"File saved: {input_path}")

        # Inkscape Command (Headless)
        # --export-type=png : Export as PNG
        # --export-filename : Output path
        # --export-dpi=96 : Standard web DPI
        command = [
            "inkscape",
            input_path,
            "--export-type=png",
            f"--export-filename={output_path}",
            "--export-dpi=96"
        ]
        
        logger.info("Starting Inkscape conversion...")
        subprocess.run(command, check=True, timeout=60)
        logger.info("Conversion successful")

        if not os.path.exists(output_path):
             return jsonify({"error": "Conversion finished but output file missing"}), 500

        return send_file(output_path, mimetype='image/png')

    except subprocess.CalledProcessError as e:
        logger.error(f"Inkscape failed: {e}")
        return jsonify({"error": "Conversion failed. File might be corrupted or version too new."}), 500
    except subprocess.TimeoutExpired:
        logger.error("Conversion timed out")
        return jsonify({"error": "Conversion timed out (file too complex)."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    finally:
        # Cleanup
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible inside Docker
    app.run(host='0.0.0.0', port=5000)

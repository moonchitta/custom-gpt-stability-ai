from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests
import io
import os
from dotenv import load_dotenv
from uuid import uuid4

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Directory to save images
IMAGE_SAVE_DIR = "saved_images"
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

# Get the API key from environment variables
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY is not set in the .env file")

# Home endpoint to explain the API functionality
@app.route('/')
def home():
    return "<h1>Stability AI Image API</h1><p>Use /generate_image and /upscale_image endpoints.</p>"

# Endpoint for image generation
@app.route('/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/core",
            headers={
                "authorization": f"Bearer {API_KEY}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "webp",
            },
        )

        if response.status_code == 200:
            # Generate unique file name
            file_name = f"{uuid4().hex}.webp"
            file_path = os.path.join(IMAGE_SAVE_DIR, file_name)

            # Save the image locally
            with open(file_path, "wb") as file:
                file.write(response.content)

            # Return the URL to the saved image
            return jsonify({"image_url": f"/{file_path}"})
        else:
            return jsonify({"error": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for image upscaling
@app.route('/upscale_image', methods=['POST'])
def upscale_image():
    if 'image' not in request.files:
        return jsonify({"error": "Image file is required"}), 400

    image_file = request.files['image']
    try:
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/upscale/fast",
            headers={
                "authorization": f"Bearer {API_KEY}",
                "accept": "image/*"
            },
            files={
                "image": image_file.stream
            },
            data={
                "output_format": "webp",
            },
        )

        if response.status_code == 200:
            # Generate unique file name
            file_name = f"{uuid4().hex}.webp"
            file_path = os.path.join(IMAGE_SAVE_DIR, file_name)

            # Save the image locally
            with open(file_path, "wb") as file:
                file.write(response.content)

            # Return the URL to the saved image
            return jsonify({"image_url": f"/{file_path}"})
        else:
            return jsonify({"error": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve saved images
@app.route('/saved_images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_SAVE_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, jsonify, render_template_string, send_from_directory, make_response
import requests
import io
import os
from dotenv import load_dotenv
from uuid import uuid4
import logging

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

# Add ngrok-skip-browser-warning to all responses
@app.after_request
def add_ngrok_skip_header(response):
    """Add the ngrok-skip-browser-warning header to all responses."""
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

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
                "output_format": "png",
            },
        )

        if response.status_code == 200:
            # Generate unique file name
            file_name = f"{uuid4().hex}.png"
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


logging.basicConfig(level=logging.DEBUG)

# Endpoint for image upscaling
@app.route('/upscale_image', methods=['POST'])
def upscale_image():
    logging.debug("Request received at /upscale_image endpoint.")

    # Validate input
    data = request.json
    if not data or "image_url" not in data:
        logging.error("Image URL not provided in the request.")
        return jsonify({"error": "Image URL is required"}), 400

    image_url = data["image_url"]
    logging.debug(f"Image URL received: {image_url}")

    try:
        # Download the image from the URL
        logging.debug(f"Downloading image from URL: {image_url}")
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            logging.error(f"Failed to download image. Status code: {image_response.status_code}")
            return jsonify({"error": "Failed to download image from the provided URL"}), 400

        # Prepare the image for Stability AI
        image_file = io.BytesIO(image_response.content)
        image_file.name = "downloaded_image"  # Necessary for some APIs that expect file names

        # Send the image to Stability AI for upscaling
        logging.debug("Sending image to Stability AI for upscaling.")
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/upscale/fast",
            headers={
                "authorization": f"Bearer {API_KEY}",
                "accept": "image/*"
            },
            files={
                "image": image_file
            },
            data={
                "output_format": "png",
            },
        )

        # Log response status
        logging.debug(f"Response status code from Stability AI: {response.status_code}")

        if response.status_code == 200:
            # Generate unique file name
            file_name = f"{uuid4().hex}.png"
            file_path = os.path.join(IMAGE_SAVE_DIR, file_name)

            # Save the upscaled image locally
            with open(file_path, "wb") as file:
                file.write(response.content)
            logging.info(f"Upscaled image saved successfully as '{file_path}'.")

            # Return the URL to the saved image
            return jsonify({"image_url": f"/{file_path}"})
        else:
            # Log response details if not successful
            logging.error(f"Error response from Stability AI: {response.text}")
            return jsonify({"error": response.json()}), response.status_code

    except Exception as e:
        logging.exception("An exception occurred while processing the request.")
        return jsonify({"error": str(e)}), 500

# Serve saved images
@app.route('/saved_images/<filename>')
def serve_image(filename):
    try:
        # Serve the file from the directory
        response = make_response(send_from_directory(IMAGE_SAVE_DIR, filename))

        # Add the ngrok-skip-browser-warning header
        response.headers["ngrok-skip-browser-warning"] = "true"

        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

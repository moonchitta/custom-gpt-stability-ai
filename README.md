# **Stability AI Image API**

This project provides a Flask-based API to interact with Stability AI services. It supports generating images from text prompts and upscaling images to enhance their resolution. The API saves generated or upscaled images locally and returns their URLs for easy access.

---

## **Features**
- **Image Generation**: Generate images based on user-provided text prompts.
- **Image Upscaling**: Enhance the resolution of uploaded images.
- **Image URLs**: Returns a URL pointing to the saved image, making it easy to integrate with external applications.
- **Local Storage**: Saves generated or upscaled images in a `saved_images` directory.

---

## **Endpoints**

### 1. **Generate Image**
   - **URL**: `/generate_image`
   - **Method**: `POST`
   - **Description**: Generates an image based on a text prompt.
   - **Request Body**:
     ```json
     {
         "prompt": "A futuristic cityscape at night"
     }
     ```
   - **Response**:
     ```json
     {
         "image_url": "/saved_images/<unique_file_name>.webp"
     }
     ```

### 2. **Upscale Image**
   - **URL**: `/upscale_image`
   - **Method**: `POST`
   - **Description**: Upscales an uploaded image. The input image must not exceed 512x512 pixels.
   - **Request**:
     - `multipart/form-data` with a key `image` containing the image file.
   - **Response**:
     ```json
     {
         "image_url": "/saved_images/<unique_file_name>.webp"
     }
     ```

---

## **Setup and Installation**

### Prerequisites
- Python 3.9+
- Stability AI API Key (Add to `.env` file)

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://vmi2238118.contaboserver.net/hammad/custom-gpt-stability-ai
   cd stability-ai-image-api
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` File**:
   - Add your Stability AI API key:
     ```
     API_KEY=your_stability_ai_api_key
     ```

5. **Run the Server**:
   ```bash
   python app.py
   ```

6. **Access the API**:
   - The API will run on `http://127.0.0.1:5000`.

---

## **Testing the Endpoints**

### Generate Image
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"prompt": "A magical forest"}' \
http://127.0.0.1:5000/generate_image
```

### Upscale Image
```bash
curl -X POST -F "image=@low-res-photo.jpg" \
http://127.0.0.1:5000/upscale_image
```

---

## **Directory Structure**
```
stability-ai-image-api/
│
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── saved_images/            # Directory to store images
└── README.md                # Documentation
```

---

## **Error Handling**

### Common Errors
1. **Invalid Input**:
   - **Cause**: Missing `prompt` or image file.
   - **Response**:
     ```json
     {
         "error": "Prompt is required"
     }
     ```

2. **Image Too Large**:
   - **Cause**: Uploaded image exceeds 512x512 pixels.
   - **Response**:
     ```json
     {
         "error": "Image dimensions should not exceed 512x512"
     }
     ```

3. **Server Error**:
   - **Cause**: Issues with Stability AI services.
   - **Response**:
     ```json
     {
         "error": "Server error message"
     }
     ```

---

## **Future Enhancements**
- Support additional image formats (e.g., `.png`, `.jpeg`).
- Add authentication for secure API access.
- Extend functionality to allow batch image processing.

---

## **Contributing**
Contributions are welcome! Feel free to fork the repository, make changes, and submit a pull request.

---

## **License**
This project is licensed under the MIT License.

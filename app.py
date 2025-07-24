import os
from flask import Flask, request, render_template, jsonify
from PIL import Image
import google.generativeai as genai
from werkzeug.utils import secure_filename

# 🔐 Set your Gemini API key here or via environment variables
GOOGLE_API_KEY = "AIzaSyCNAOwucDS-4FAOWpKzvZVh9k_69R022To"
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create the upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Text prompt handler
def send_text_request(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    return response.text

# Image analysis handler
def image_analysis_request(image_path):
    model = genai.GenerativeModel("gemini-pro-vision")
    image = Image.open(image_path)
    response = model.generate_content(["Analyze the image in detail:", image])
    return response.text

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Handle text-based questions
@app.route('/get-answer', methods=['POST'])
def get_answer():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'answer': 'No question received'})
    answer = send_text_request(question)
    return jsonify({'answer': answer})

# Handle image upload and analysis
@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'answer': 'No image uploaded'})

    image = request.files['image']
    if image.filename == '':
        return jsonify({'answer': 'Empty image file'})

    filename = secure_filename(image.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(path)

    answer = image_analysis_request(path)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request
import re
import easyocr
import requests
from io import BytesIO

app = Flask(__name__)

def extract_coordinates(text):
    # Regular expression to find latitude and longitude patterns
    pattern = r'Lat\s*(-?\d+\.\d+)\s*Long\s*(-?\d+\.\d+)'

    # Search for the pattern in the text
    matches = re.search(pattern, text)

    # If matches are found, return latitude and longitude
    if matches:
        return matches.group(1), matches.group(2)
    else:
        return None

def get_address_from_coords(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    
    response = requests.get(url)
    data = response.json()
    
    if 'display_name' in data:
        return data['display_name']
    else:
        return "Unable to retrieve address"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    # Convert file object to bytes
    image_bytes = BytesIO()
    file.save(image_bytes)
    
    # Initialize the OCR reader
    reader = easyocr.Reader(['en'])  # Specify language(s) for text recognition, e.g., ['en'] for English

    # Read text from the image
    result = reader.readtext(image_bytes.getvalue())

    # Extract text from the result
    extracted_text = ''
    for detection in result:
        extracted_text += detection[1] + ' '

    coordinates = extract_coordinates(extracted_text)
    if coordinates:
        latitude, longitude = coordinates
        address = get_address_from_coords(latitude, longitude)
        return f"Address: {address}"
    else:
        return "No coordinates found in the extracted text."

if __name__ == '__main__':
    app.run(debug=True)

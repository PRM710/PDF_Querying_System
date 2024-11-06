from flask import Flask, request, jsonify
import boto3
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
import firebase_admin
from firebase_admin import credentials, firestore
import openai
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://prmquerying.netlify.app", "http://localhost:3000"])

# Get AWS credentials from environment variables
BUCKET_NAME = 'prakashprm'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
)

# Initialize Firebase
firebase_config = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace('\\n', '\n'),  # Ensure line breaks are handled
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN")
}
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def upload_pdf(file_path, bucket_name):
    """Upload a PDF file to the specified S3 bucket."""
    try:
        pdf_key = os.path.basename(file_path)
        s3.upload_file(file_path, bucket_name, pdf_key)
        return pdf_key
    except Exception as e:
        print(f"Error uploading PDF file: {e}")
        return None

def list_pdf_files(bucket_name):
    """Retrieve and list PDF files from the specified S3 bucket."""
    pdf_files = []
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            pdf_files = [item['Key'] for item in response['Contents'] if item['Key'].endswith('.pdf')]
    except Exception as e:
        print(f"Error retrieving PDF files: {e}")
    return pdf_files

def download_pdf(bucket_name, pdf_key):
    """Download PDF file from S3 and return the local file path."""
    local_pdf_path = os.path.join('./uploads', pdf_key.split('/')[-1])
    try:
        s3.download_file(bucket_name, pdf_key, local_pdf_path)
        return local_pdf_path
    except Exception as e:
        print(f"Error downloading PDF file: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """Extract text from the PDF using PyMuPDF."""
    text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page_num in range(pdf.page_count):
                text += pdf[page_num].get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def store_text_in_firebase(text, pdf_name):
    """Store extracted text in Firebase Firestore."""
    try:
        db.collection("pdf_texts").document(pdf_name).set({"text": text})
    except Exception as e:
        print(f"Error storing text in Firebase: {e}")

def ask_questions(pdf_text, questions):
    """Allow the user to ask multiple questions about the extracted PDF text using OpenAI API."""
    questions_and_answers = []
    for question in questions:
        if not question:
            continue
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are an assistant that answers questions based on PDF content."},
                          {"role": "user", "content": f"PDF Content:\n{pdf_text}\n\nQuestion: {question}"}],
                max_tokens=100,
                temperature=0.5
            )
            answer = response.choices[0].message['content'].strip()
            questions_and_answers.append({"question": question, "answer": answer})
        except Exception as e:
            print(f"Error in OpenAI API request: {e}")
    return questions_and_answers

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and call upload_pdf function."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    os.makedirs('./uploads', exist_ok=True)

    file_path = f"./uploads/{file.filename}"
    file.save(file_path)
    
    pdf_key = upload_pdf(file_path, BUCKET_NAME)
    if pdf_key:
        return jsonify({"message": "Upload successful", "pdf_key": pdf_key}), 200
    else:
        return jsonify({"error": "Upload failed"}), 500

@app.route('/pdfs', methods=['GET'])
def list_pdfs():
    """Call list_pdf_files function and return the list of PDFs."""
    pdf_files = list_pdf_files(BUCKET_NAME)
    return jsonify({"pdf_files": pdf_files}), 200

@app.route('/pdf/<pdf_key>', methods=['GET'])
def download_pdf_route(pdf_key):
    """Call download_pdf function and return the content or status."""
    local_pdf_path = download_pdf(BUCKET_NAME, pdf_key)
    if local_pdf_path:
        return jsonify({"message": "Download successful", "local_path": local_pdf_path}), 200
    else:
        return jsonify({"error": "Download failed"}), 500

@app.route('/extract', methods=['POST'])
def extract_text():
    """Call extract_text_from_pdf function and return the extracted text."""
    pdf_key = request.json.get('pdf_key')
    local_pdf_path = download_pdf(BUCKET_NAME, pdf_key)
    
    if local_pdf_path:
        extracted_text = extract_text_from_pdf(local_pdf_path)
        if extracted_text:
            store_text_in_firebase(extracted_text, pdf_key)
            return jsonify({"message": "Text extracted and stored successfully", "text": extracted_text}), 200
        else:
            return jsonify({"error": "No text extracted from the PDF"}), 500
    else:
        return jsonify({"error": "Failed to download the PDF"}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle question asking and call ask_questions function."""
    pdf_key = request.json.get('pdf_key')
    questions = request.json.get('questions', [])
    local_pdf_path = download_pdf(BUCKET_NAME, pdf_key)
    
    if local_pdf_path:
        pdf_text = extract_text_from_pdf(local_pdf_path)
        if pdf_text:
            questions_and_answers = ask_questions(pdf_text, questions)
            return jsonify({"message": "Questions answered successfully", "qa": questions_and_answers}), 200
        else:
            return jsonify({"error": "No text extracted from the PDF"}), 500
    else:
        return jsonify({"error": "Failed to download the PDF"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT is not set
    app.run(host="0.0.0.0", port=port, debug=True)

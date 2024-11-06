
# PDF-Querying-System

This project integrates AWS S3, OpenAI, and Firebase for document processing and interactive Q&A functionality. Using React for the frontend and FastAPI for backend services, it provides an environment for document management, text extraction, and responsive user interaction.

## Prerequisites

Before starting, make sure you have:

- Python (preferably version 3.8 or higher)
- Node.js and npm
- AWS and Firebase accounts

## Environment Setup

### Environment Variables

Create an `.env` file in the `/src` directory with the following content:

```
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=your-default-region
OPENAI_API_KEY=your-openai-api-key
```

### Firebase Key File

Generate a Firebase key file (`key.json`) by following these steps:

1. Go to Firebase Console.
2. Select Project Settings > Service Accounts.
3. Generate a new private key.
4. Save this file in the `/src` directory as `key.json`.

## Installation

### Backend (Python)

1. Go to the backend directory:

    ```bash
    cd src
    ```

2. Install required Python libraries with `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

    Or install individually:

    ```bash
    pip install Flask Flask-CORS python-dotenv boto3 firebase-admin PyMuPDF openai
    ```

### Frontend (React)

1. Open a new terminal.
2. Install required npm packages:

    ```bash
    npm install react react-dom react-scripts axios
    ```

## Running the Application

To start the application, follow these steps:

1. In one terminal, navigate to the backend directory and start the Flask server:

    ```bash
    cd src
    python app.py
    ```

2. In another terminal, start the React frontend:

    ```bash
    npm start/run
    ```

3. Open the link provided in the terminal, or wait for it to open automatically in the browser.

Your application should now be running successfully!

---

Thank you! Enjoy using the application!

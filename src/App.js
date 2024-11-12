import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; // Ensure to import your CSS file

function App() {
    const [pdfFiles, setPdfFiles] = useState([]);
    const [selectedPdf, setSelectedPdf] = useState('');
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [isLoading, setIsLoading] = useState(false); // Loading state

    // Fetch PDF files when the component mounts
    useEffect(() => {
        const fetchPdfFiles = async () => {
            try {
                const response = await axios.get('http://localhost:5000/pdfs');
                setPdfFiles(response.data.pdf_files);
            } catch (error) {
                console.error('Error fetching PDF files:', error);
            }
        };
        fetchPdfFiles();
    }, []);

    // Handle selection of a PDF file
    const handlePdfSelect = (pdf) => {
        setSelectedPdf(pdf);
    };

    // Ask a question related to the selected PDF
    const askQuestion = async () => {
        if (!question.trim()) {
            setAnswer("Please enter a valid question.");
            return;
        }

        setIsLoading(true); // Start loading
        setAnswer(''); // Clear previous answer

        try {
            const response = await axios.post('http://localhost:5000/ask', { pdf_key: selectedPdf, questions: [question] });

            if (response.data.qa && response.data.qa.length > 0) {
                setAnswer(response.data.qa[0].answer);
            } else {
                setAnswer("No answer available.");
            }
        } catch (error) {
            console.error("Error asking question:", error);
            setAnswer("Sorry, there was an error. Please try again.");
        } finally {
            setIsLoading(false); // Stop loading
        }

        setQuestion(''); // Clear the question input
    };

    // Handle file upload
    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:5000/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            console.log(response.data);

            // Refresh the list of PDF files after upload
            fetchPdfFiles();
        } catch (error) {
            console.error('Error uploading PDF:', error);
        }
    };

    // Refresh the list of PDF files after an upload
    const fetchPdfFiles = async () => {
        try {
            const response = await axios.get('http://localhost:5000/pdfs');
            setPdfFiles(response.data.pdf_files);
        } catch (error) {
            console.error('Error fetching PDF files:', error);
        }
    };

    return (
        <div className="container">
            {/* Logo Section */}
            <img src={`${process.env.PUBLIC_URL}/prm.png`} alt="Logo" className="logo-image" />

            <div className="upload-section">
                <input
                    type="file"
                    accept="application/pdf"
                    id="file-upload"
                    style={{ display: 'none' }} // Hide the default file input
                    onChange={handleFileUpload}
                />
                <label htmlFor="file-upload" className="upload-label">
                    <img src={`${process.env.PUBLIC_URL}/upload.png`} alt="Upload PDF" className="png-image" />
                </label>
            </div>

            {/* PDF Files List */}
            <div className="pdf-list">
                <h4>Available PDFs</h4>
                <ul>
                    {pdfFiles.map((pdf, index) => (
                        <li key={index} onClick={() => handlePdfSelect(pdf)}>
                            {pdf}
                        </li>
                    ))}
                </ul>
            </div>

            {/* Chatbox Section */}
            {selectedPdf && (
                <div className="chatbox">
                    <h4>SELECTED PDF: {selectedPdf}</h4>

                    <input
                        type="text"
                        className="question-input"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Type your question here"
                    />

                    <button onClick={askQuestion} disabled={isLoading}>
                        {isLoading ? 'Asking...' : 'Ask'}
                    </button>

                    {/* Display Answer */}
                    {answer && (
                        <div className="answer">
                            <p>Answer: {answer}</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default App;

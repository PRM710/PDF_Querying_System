import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'; // Ensure to import your CSS file

function App() {
    const [pdfFiles, setPdfFiles] = useState([]);
    const [selectedPdf, setSelectedPdf] = useState('');
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');

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

    const handlePdfSelect = (pdf) => {
        setSelectedPdf(pdf);
    };

    const askQuestion = async () => {
        if (!question) return;
        try {
            const response = await axios.post('http://localhost:5000/ask', { pdf_key: selectedPdf, questions: [question] });
            if (response.data.qa && response.data.qa.length > 0) {
                setAnswer(response.data.qa[0].answer);
            } else {
                setAnswer("No answer available.");
            }
            setQuestion(''); // Clear the question after asking
        } catch (error) {
            console.error("Error asking question:", error);
        }
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await axios.post('http://localhost:5000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            console.log(response.data);
            // Refresh PDF list after upload
            const fetchPdfFiles = async () => {
                const res = await axios.get('http://localhost:5000/pdfs');
                setPdfFiles(res.data.pdf_files);
            };
            fetchPdfFiles();
        } catch (error) {
            console.error('Error uploading PDF:', error);
        }
    };

    return (
        <div className="container">
            {/* Logo Section */}
            <img src={`${process.env.PUBLIC_URL}/aiplanet.png`} alt="Logo" className="logo-image" /> {/* Update with your logo file name */}
            
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
            {selectedPdf && (
                <div className="chatbox">
                    <h4>SELECT PDF: {selectedPdf}</h4>
                    <input
                        type="text"
                        className="question-input"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Type your question here"
                    />
                    <button onClick={askQuestion}>Ask</button>
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

import React, { useState } from 'react';
import './App.css';
import logo from './aiplanetlogo.png'; 

function App() {
  const [pdfFile, setPdfFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [conversation, setConversation] = useState([]);
  const [documentId, setDocumentId] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    setPdfFile(file);

    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setDocumentId(data.file_id); 
        console.log('File uploaded successfully:', data);
      } else {
        console.error('File upload failed:', data.detail);
        alert('File upload failed: ' + data.detail);
      }
    } catch (error) {
      console.error('Error during file upload:', error);
      alert('Error during file upload: ' + error.message);
    }
  };

  const handleAskQuestion = async () => {
    if (!documentId) {
      alert("Please upload a PDF first.");
      return;
    }
    if (!question.trim()) {
      alert("Please enter a question.");
      return;
    }

    try {
      console.log(documentId, question);
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ document_id: documentId, question: question }),
      });

      const data = await response.json();

      if (response.ok) {
        const newResponse = {
          question: question,
          answer: data.answer || 'No answer available',
        };
        setConversation([...conversation, newResponse]);
        setQuestion('');
      } else {
        console.error('Error asking question:', data.detail);
        alert('Error asking question: ' + data.detail);
      }
    } catch (error) {
      console.error('Error during question API call:', error);
      alert('Error during question API call: ' + error.message);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-left">
          <img src={logo} alt="Company Logo" className="company-logo" />
        </div>
        <div className="header-right">
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileUpload}
            className="pdf-upload-button"
          />
        </div>
      </header>

      <main className="App-main">
        <div className="conversation-section">
          {conversation.map((entry, index) => (
            <div key={index} className="qna-box">
              <div className="message">
                <span className="icon">💬</span>
                <span className="qna-text"> {entry.question}</span>
              </div>
              <div className="response">
                <div classname="logo-icon"><span className="icon"><img src="/Assets/logo.gif" alt="Logo" /></span></div>
                <span className="qna-text"> {entry.answer}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="question-section">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)} // 💬 🤖
            placeholder="Ask a question..."
            className="question-input"
          />
          <button onClick={handleAskQuestion} className="send-button">
          <img src="/Assets/send-icon.png" height={30} />
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;

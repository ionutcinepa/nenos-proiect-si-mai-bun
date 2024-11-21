import React, { useState } from 'react';
import QuestionInput from './components/QuestionInput';
import './App.css';

const App = () => {
  const [documentSummary, setDocumentSummary] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [history, setHistory] = useState([]); // History for conversation

  const handleFileUpload = (summary, error) => {
    setDocumentSummary(summary || '');
    setErrorMessage(error || '');
  };

  const handleQuestionResponse = (question, cohere, nlpCloud) => {
    // Update conversation history
    setHistory((prevHistory) => [
      ...prevHistory,
      {
        type: 'user',
        content: question,
      },
      ...(cohere ? [{ type: 'cohere', content: cohere }] : []),
      ...(nlpCloud ? [{ type: 'nlpCloud', content: nlpCloud }] : []),
    ]);
  };

  return (
    <div className="app-container">
      {/* Header Section */}
      <header className="header">
        <h1>AI Assistant</h1>
      </header>

      {/* Main Content Section */}
      <main className="content">
        {errorMessage && <p className="error">{errorMessage}</p>}
        {documentSummary && <p className="summary">{documentSummary}</p>}
        <div className="chat-history">
          {history.map((entry, index) => (
            <div
              key={index}
              className={`chat-entry ${
                entry.type === 'user'
                  ? 'chat-user'
                  : entry.type === 'cohere'
                  ? 'chat-cohere'
                  : 'chat-nlp'
              }`}
            >
              <p>{entry.content}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Bottom Bar Section */}
      <div className="bottom-bar">
        <QuestionInput onFileUpload={handleFileUpload} onResponse={handleQuestionResponse} />
      </div>
    </div>
  );
};

export default App;

import React, { useState } from 'react';
import FileUpload from './FileUpload';

const QuestionInput = ({ onResponse, onFileUpload }) => {
  const [question, setQuestion] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Fetch the document summary from the backend
      const summaryResponse = await fetch('http://127.0.0.1:8000/summary');
      if (!summaryResponse.ok) {
        throw new Error('Failed to fetch document summary');
      }

      const summaryData = await summaryResponse.json();
      if (!summaryData.summary) {
        throw new Error('Summary not found in backend response');
      }

      const summary = summaryData.summary;

      // Submit the question and summary to the backend
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, summary }),
      });

      if (!response.ok) {
        throw new Error('Error in response from /ask endpoint');
      }

      const data = await response.json();
      // Pass the question and responses back to the parent component
      onResponse(question, data.cohere_answer, data.nlp_cloud_answer);
      setQuestion(''); // Clear input after submission
    } catch (error) {
      console.error('Error fetching responses:', error);
      alert(error.message); // Notify user of the error
    }
  };

  return (
    <form onSubmit={handleSubmit} className="question-input-form">
      {/* Upload Button */}
      <FileUpload onFileUpload={onFileUpload} />

      {/* Text Area */}
      <textarea
        className="textarea"
        placeholder="Ask your question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      {/* Ask Button */}
      <button type="submit" className="ask-button">Ask</button>
    </form>
  );
};

export default QuestionInput;

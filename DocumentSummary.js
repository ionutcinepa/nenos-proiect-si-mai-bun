import React from 'react';

const DocumentSummary = ({ summary }) => (
  <div className="response">
    {summary ? (
      <>
        <h2>Document Summary:</h2>
        <p>{summary}</p>
      </>
    ) : (
      <p>No summary available. Please upload a document.</p>
    )}
  </div>
);

export default DocumentSummary;

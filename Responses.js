import React from 'react';

const Responses = ({ cohereAnswer, nlpCloudAnswer }) => (
  <div className="response">
    {cohereAnswer || nlpCloudAnswer ? (
      <>
        {cohereAnswer && (
          <>
            <h2>Cohere Answer:</h2>
            <p>{cohereAnswer}</p>
          </>
        )}
        {nlpCloudAnswer && (
          <>
            <h2>NLP Cloud Answer:</h2>
            <p>{nlpCloudAnswer}</p>
          </>
        )}
      </>
    ) : (
      <p>No responses available. Please ask a question.</p>
    )}
  </div>
);

export default Responses;

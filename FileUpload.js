import React, { useState } from 'react';

const FileUpload = ({ onFileUpload }) => {
  const [file, setFile] = useState(null);
  const [successMessage, setSuccessMessage] = useState(''); // State for success message

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("sending file...");

    if (!file) {
      console.error("No file selected!");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', { method: 'POST', body: formData });
      const data = await response.json();
      onFileUpload(data.summary, null);

      // Show success message
      setSuccessMessage('File uploaded successfully!');
      setTimeout(() => setSuccessMessage(''), 3000); // Hide message after 3 seconds
    } catch (error) {
      console.error("Error during upload:", error);
      onFileUpload(null, 'Error uploading file');
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="file-upload-form">
        <label htmlFor="file-upload" className="upload-button">+</label>
        <input
          type="file"
          id="file-upload"
          accept="application/pdf"
          style={{ display: 'none' }}
          onChange={(e) => {
            setFile(e.target.files[0]);
            console.log("Selected file:", e.target.files[0]);
          }}
          required
        />
      </form>
      {/* Success Toast */}
      {successMessage && <div className="toast show">{successMessage}</div>}
    </div>
  );
};

export default FileUpload;



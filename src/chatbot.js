
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import './chatbot.css';
import logo from './logo.svg';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const onDrop = (acceptedFiles) => {
    setUploadedFiles([...uploadedFiles, ...acceptedFiles]);
  };

  const { getRootProps, getInputProps } = useDropzone({
    accept: { 'application/pdf': [] },
    onDrop
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      setMessages([...messages, { text: input, sender: 'user' }]);
      setInput('');
    }
  };

  return (
    <div className="chatbot-container">
      {/* Add the logo at the top left corner */}
      <div className="logo-container">
        <img src={logo} alt="Logo" className="site-logo" />
      </div>

      <div className="chatbox">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}>
            {message.text}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
        />
        <button type="submit" className="send-button">Send</button>
      </form>

      <div {...getRootProps()} className="upload-area">
        <input {...getInputProps()} />
        <p>Drag and drop PDF files here, or click to select files</p>
      </div>

      <div className="uploaded-files">
        {uploadedFiles.map((file, index) => (
          <p key={index} className="file-name">{file.name}</p>
        ))}
      </div>
    </div>
  );
};

export default Chatbot;

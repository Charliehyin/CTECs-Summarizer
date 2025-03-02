import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

const OpenAIResponse = ({ response }) => {
  const cleanedResponse = response.replace(/【\d+:\d+†source】/g, "")
  return (
    <div>
      {cleanedResponse.split("\n").map((line, index) => {
        if (line.match(/\*\*(.*?)\*\*/)) {
          return <h3 key={index}>{line.replace(/\*\*(.*?)\*\*/, "$1").replace(/\*\*(.*?)\*\*/g, "$1")}</h3>;
        } else if (line.startsWith("- ")) {
          return <li key={index}>{line.substring(2).replace(/\*\*(.*?)\*\*/g, "$1")}</li>;
        } else {
          return <p key={index}>{line}</p>;
        }
      })}
    </div>
  );
};

const ChatMessage = ({ message, isUser }) => (
  <div className={`message ${isUser ? 'user' : ''}`}>
    <div className="message-content">
      {isUser ? message : <OpenAIResponse response={message} />}
    </div>
  </div>
);

const CourseChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();
      setMessages((prev) => [...prev, { text: data.response, isUser: false }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { text: 'Sorry, there was an error processing your request.', isUser: false },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        <h1 className="chat-header">Northwestern Course Assistant</h1>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-title">
                Welcome! Ask me anything about Northwestern courses.
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message.text}
                isUser={message.isUser}
              />
            ))
          )}

          {isLoading && (
            <div className="loading-message">
              <div className="assistant-message">
                <span>Generating a response</span>
                <span className="loading-dots">
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="chat-form">
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type here..."
            disabled={isLoading}
          />
          <button type="submit" className="submit-button" disabled={isLoading}>
            <Send size={24} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default CourseChatbot;
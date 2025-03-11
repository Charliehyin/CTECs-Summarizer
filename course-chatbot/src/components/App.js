import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import Login from './Login';
import About from './About';

const OpenAIResponse = ({ response }) => {
  const cleanedResponse = response.replace(/【\d+:\d+†source】/g, "");
  
  return (
    <div className="response-content">
      {cleanedResponse.split("\n").map((line, index) => {
        const unboldedLine = line.replace(/\*\*/g, "");
        
        const numberedMatch = unboldedLine.match(/^(\d+)\.\s+(.*)/);
        
        if (numberedMatch) {
          return (
            <div key={index} className="numbered-item">
              <span className="item-number">{numberedMatch[1]}.</span>
              <span className="item-content">{numberedMatch[2]}</span>
            </div>
          );
        } else if (unboldedLine.startsWith("- ")) {
          return <li key={index}>{unboldedLine.substring(2)}</li>;
        } else if (unboldedLine.trim() === "") {
          return <br key={index} />;
        } else {
          return <p key={index}>{unboldedLine}</p>;
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

const App = () => {
  const [user, setUser] = useState(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showGreeting, setShowGreeting] = useState(true);
  const [showAbout, setShowAbout] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);
  
  const handleLogin = (userData) => {
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };
  
  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setMessages([]);
    setIsExpanded(false);
    setShowGreeting(true);
  };

  const handleNewChat = () => {
    setMessages([]);
    setIsExpanded(false);
    setShowGreeting(true);
    setInput('');
  };

  const handleAboutClick = () => {
    setShowAbout(true);
  };

  const handleCloseAbout = () => {
    setShowAbout(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Expand the chat if this is the first message
    if (!isExpanded) {
      setIsExpanded(true);
      setShowGreeting(false);
    }

    const userMessage = input.trim();
    setInput(''); // Clear input field
    setMessages((prev) => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);
    
    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: userMessage,
          user: user?.email || 'guest'
        }),
      });

      if (!response.ok) {
        throw new Error(`API responded with status: ${response.status}`);
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { text: data.response, isUser: false }]);
    } catch (error) {
      console.error('Error details:', error);
      setMessages((prev) => [
        ...prev,
        { text: `Sorry, there was an error processing your request. Please make sure the backend server is running.`, isUser: false },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputFocus = () => {
    // Don't expand on focus if there are no messages yet
    if (messages.length > 0 && !isExpanded) {
      setIsExpanded(true);
      setShowGreeting(false);
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // If no user is logged in, show the Login component
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }
  
  // Otherwise, show the main application
  return (
    <div className="app-container">
      {showAbout && <About onClose={handleCloseAbout} />}
      
      <div className="user-info">
        <button onClick={handleNewChat} className="logout-button" style={{ marginRight: 'auto' }}>New Chat</button>
        <button onClick={handleAboutClick} className="about-button" style={{ marginRight: 'auto' }}>About</button>
        {user.picture && (
          <img 
            src={user.picture} 
            alt={user.name} 
            className="user-avatar" 
          />
        )}
        <span className="user-name">{user.name}</span>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </div>
      
      <div className={`chat-container ${isExpanded ? 'expanded' : 'centered'}`}>
        <div className="chat-box">
          {isExpanded && (
            <h1 className="chat-header">Northwestern CTECs Assistant</h1>
          )}
          
          {isExpanded && (
            <div className="messages-container">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message.text}
                  isUser={message.isUser}
                />
              ))}

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
          )}
          
          <div className={`chat-form-container ${isExpanded ? '' : 'centered'}`}>
            {!isExpanded && showGreeting && (
              <div className="user-greeting">
                <h3>Welcome, {user.name.split(' ')[0]}</h3>
              </div>
            )}
            
            {!isExpanded && (
              <h2 className="chat-prompt">Northwestern CTECs Assistant</h2>
            )}
            
            <form onSubmit={handleSubmit} className="chat-form">
              <input
                ref={inputRef}
                type="text"
                className="chat-input"
                value={input}
                onChange={handleInputChange}
                onFocus={handleInputFocus}
                placeholder={isExpanded ? "Type here..." : "Ask me anything about Northwestern courses..."}
                disabled={isLoading}
              />
              <button type="submit" className="submit-button" disabled={isLoading || !input.trim()}>
                <Send size={24} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
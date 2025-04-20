import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import Login from './Login';
import About from './About';

const api_base_url = process.env.REACT_APP_API_BASE_URL;

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

    if (!isExpanded) {
      setIsExpanded(true);
      setShowGreeting(false);
    }

    let userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);
    
    // RAG API call
    try {
      const response = await fetch(`${api_base_url}/rag`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ 
          message: userMessage,
          top_k: 10
        }),
      });

      if (!response.ok) {
        throw new Error(`API responded with status: ${response.status}`);
      }

      const data = await response.json();
      // store RAG response data
      const ragResponse = data.response;
      
      const promptInstructions = "Please quote information you used from the context to answer the user query, if relevant.";
      userMessage = `Context from course reviews:\n${ragResponse}\n\nUser query: ${userMessage}\n\n${promptInstructions}`;
      
    } catch (error) {
      console.error('Error details:', error);
      setMessages((prev) => [
        ...prev,
        { text: `Sorry, there was an error processing your request. Please make sure the backend server for RAGis running.`, isUser: false },
      ]);
    } finally {
        // chat API call
        try {
            setMessages((prev) => [...prev, { text: "", isUser: false, isStreaming: true }]);
            
            const encodedMessage = encodeURIComponent(userMessage);
            const encodedUser = encodeURIComponent(user?.email || 'guest');
            
            const eventSource = new EventSource(
                `${api_base_url}/chat-stream?message=${encodedMessage}&user=${encodedUser}`
            );
            
            const messageIndex = messages.length;
            
            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.done) {
                        // streaming is complete
                        setMessages((prev) => {
                            const newMessages = [...prev];
                            const lastMessage = newMessages[newMessages.length - 1];
                            if (!lastMessage.isUser) {
                                lastMessage.isStreaming = false;
                            }
                            return newMessages;
                        });
                        eventSource.close();
                        setIsLoading(false);
                    } else if (data.chunk) {
                        // append chunk to the current message
                        setMessages((prev) => {
                            const newMessages = [...prev];
                            const lastMessage = newMessages[newMessages.length - 1];
                            if (!lastMessage.isUser) {
                                lastMessage.text += data.chunk;
                            }
                            return newMessages;
                        });
                    } else if (data.complete) {
                        // if we ever need to send the complete message at once
                        setMessages((prev) => {
                            const newMessages = [...prev];
                            newMessages[newMessages.length - 1] = {
                                text: data.complete,
                                isUser: false,
                                isStreaming: false
                            };
                            return newMessages;
                        });
                        eventSource.close();
                        setIsLoading(false);
                    }
                } catch (error) {
                    console.error("Error parsing event data:", error);
                }
            };
            
            eventSource.onerror = (error) => {
                console.error("EventSource error:", error);
                eventSource.close();
                setIsLoading(false);
                setMessages((prev) => [
                    ...prev,
                    { text: `Sorry, there was an error processing your request.`, isUser: false },
                ]);
            };
        } catch (error) {
            console.error('Error details:', error);
            setMessages((prev) => [
                ...prev,
                { text: `Sorry, there was an error processing your request. Please make sure the backend server is running.`, isUser: false },
            ]);
            setIsLoading(false);
        }
    }
  };
    

  const handleInputFocus = () => {
    if (messages.length > 0 && !isExpanded) {
      setIsExpanded(true);
      setShowGreeting(false);
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // if no user is logged in, show the login component
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }
  
  // otherwise show the main application
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
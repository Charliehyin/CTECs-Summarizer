import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Trash2 } from 'lucide-react';
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

const ChatHistorySidebar = ({ chatHistory, onSelectChat, onDeleteChat, activeChat }) => (
  <div className="chat-history-sidebar">
    <div className="sidebar-header">Your Chat History</div>
    <div className="chat-list">
      {chatHistory.length === 0 ? (
        <div className="no-chats">No previous chats</div>
      ) : (
        chatHistory.map((chat) => (
          <div
            key={chat.id}
            className={`chat-item ${activeChat === chat.id ? 'active' : ''}`}
            onClick={() => onSelectChat(chat)}
          >
            <div className="chat-item-icon">
              <MessageCircle size={16} />
            </div>
            <div className="chat-item-title">{chat.title || `Chat ${chat.id}`}</div>
            <button
              className="chat-item-delete"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(chat.id);
              }}
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))
      )}
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
  const [chatHistory, setChatHistory] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  useEffect(() => {
    // Fetch chat history when user logs in
    if (user) {
      fetchChatHistory();
    }
  }, [user]);

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
    console.log("Starting new chat...");
    setMessages([]);
    setIsExpanded(false);
    setShowGreeting(true);
    setInput('');
    setActiveChatId(null);
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

  const fetchChatHistory = async () => {
    try {
      const response = await fetch(`${api_base_url}/get_chat_history`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'danielkim2028@u.northwestern.edu' // Use a consistent test email
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Chat history updated:", data.chats);
        setChatHistory(data.chats || []);
      } else {
        console.error('Failed to fetch chat history');
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  const selectChat = async (chat) => {
    try {
      setActiveChatId(chat.id);
      setIsLoading(true);

      // Fetch messages for selected chat
      const response = await fetch(`${api_base_url}/get_chat_messages?chat_id=${chat.id}`);
      const data = await response.json();

      if (response.ok && Array.isArray(data)) {
        // Create a map to track unique messages
        const uniqueMessages = new Map();

        // Process each message to ensure uniqueness
        data.forEach(msg => {
          const messageKey = `${msg.message_id}-${msg.is_user ? 'user' : 'assistant'}`;

          // Only add if we haven't seen this message ID + sender combo before
          if (!uniqueMessages.has(messageKey)) {
            uniqueMessages.set(messageKey, {
              id: msg.message_id,
              text: msg.message_text,
              isUser: msg.is_user === 1,
              timestamp: new Date(msg.message_timestamp).toISOString()
            });
          }
        });

        // Convert the map values to an array and sort by message_id
        const sortedMessages = Array.from(uniqueMessages.values())
          .sort((a, b) => a.id - b.id);

        setMessages(sortedMessages);
        setIsExpanded(true);
        setShowGreeting(false);
      } else {
        console.error('Failed to load chat messages:', data.error || 'Unknown error');
        setMessages([]);
      }
    } catch (error) {
      console.error('Error selecting chat:', error);
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteChat = async (chatId) => {
    try {
      console.log("Deleting chat with ID:", chatId);
      console.log("API base URL:", api_base_url);

      // Now perform the DELETE request
      const response = await fetch(`${api_base_url}/delete_chat/${chatId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log("Delete response status:", response.status);

      // Try to parse the response
      let data;
      try {
        data = await response.json();
        console.log("Delete response data:", data);
      } catch (parseError) {
        console.warn("Could not parse response as JSON:", parseError);
      }

      if (response.ok) {
        console.log("Chat deleted successfully, updating UI");
        setChatHistory(chatHistory.filter(chat => chat.id !== chatId));
        if (activeChatId === chatId) {
          handleNewChat();
        }
        // Refetch chat history to ensure UI is in sync
        fetchChatHistory();
      } else {
        console.error("Failed to delete chat:", response.statusText);
        alert("Could not delete chat. See console for details.");
      }
    } catch (error) {
      console.error('Failed to delete chat:', error);
      // Try a fallback approach - directly update UI
      console.log("Using fallback: Updating UI without waiting for backend confirmation");
      setChatHistory(chatHistory.filter(chat => chat.id !== chatId));
      if (activeChatId === chatId) {
        handleNewChat();
      }
      // Still try to refetch history
      fetchChatHistory();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Create a chat if it doesn't exist
    let currentChatId = activeChatId;
    if (!currentChatId) {
      try {
        const createResponse = await fetch(`${api_base_url}/create_chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 'danielkim2028@u.northwestern.edu', // Use a consistent test email
            title: input.substring(0, 30) + (input.length > 30 ? '...' : '')
          }),
        });

        if (createResponse.ok) {
          const data = await createResponse.json();
          console.log("New chat created with ID:", data.chatId);
          currentChatId = data.chatId;
          setActiveChatId(currentChatId);

          // Immediately update chat history
          await fetchChatHistory();
        }
      } catch (error) {
        console.error('Failed to create chat:', error);
      }
    }

    if (!isExpanded) {
      setIsExpanded(true);
      setShowGreeting(false);
    }

    let userMessage = input.trim();
    let originalUserMessage = userMessage; // Store the original message for saving to history
    setInput('');
    setMessages((prev) => [...prev, { text: userMessage, isUser: true }]);

    // We won't set isLoading to true here anymore
    // This will prevent showing the "generating a response" indicator

    // Save user message to history first
    if (currentChatId) {
      try {
        await fetch(`${api_base_url}/save_chat_message`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            chatId: currentChatId,
            message: originalUserMessage,
            isUser: true
          }),
        });
        console.log("User message saved to chat:", currentChatId);
      } catch (error) {
        console.error('Failed to save user message:', error);
      }
    }

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
        { text: `Sorry, there was an error processing your request. Please make sure the backend server for RAG is running.`, isUser: false },
      ]);
      return;
    }

    // chat API call
    try {
      console.log("Sending request to chat-stream endpoint");
      // We need to use fetch with POST method instead of EventSource
      const response = await fetch(`${api_base_url}/chat-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage,
          chatId: currentChatId,
          user_id: 'danielkim2028@u.northwestern.edu' // Use a consistent test email
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      console.log("Got response from chat-stream, starting to read stream");

      // Use a ReadableStream to process the streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let hasStartedResponse = false;
      let lastMessageText = '';

      // Add empty response message immediately to start stream
      setMessages(prev => [...prev, {
        text: '',
        isUser: false,
        isStreaming: true
      }]);
      hasStartedResponse = true;

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log("Stream reading complete");
          break;
        }

        // Decode the chunk and split by lines (each line is an SSE event)
        const chunk = decoder.decode(value, { stream: true });
        console.log("Received chunk:", chunk);
        const lines = chunk.split('\n\n');

        for (const line of lines) {
          if (!line.trim() || !line.startsWith('data: ')) continue;

          try {
            // Parse the SSE data
            const eventData = JSON.parse(line.substring(6));
            console.log("Parsed event data:", eventData);

            // Handle "done" event
            if (eventData.done) {
              console.log("Received 'done' event");

              // We no longer need to update UI with eventData.complete
              // since we've already built the message from streaming chunks
              setIsLoading(false);

              // The assistant message is now saved in the backend
              // No need to save it again here
              break;
            }

            // Handle chunk event
            if (eventData.chunk) {
              console.log("Received chunk content:", eventData.chunk);

              // Update the existing message with new content
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (!lastMessage.isUser) {
                  lastMessage.text += eventData.chunk;
                  lastMessageText = lastMessage.text;
                }
                return newMessages;
              });
            }
          } catch (error) {
            console.error("Error parsing event data:", error);
          }
        }
      }
    } catch (error) {
      console.error('Error details:', error);
      setMessages((prev) => [
        ...prev,
        { text: `Sorry, there was an error processing your request. Please make sure the backend server is running.`, isUser: false },
      ]);
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

  const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
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
        <div className="left-buttons">
          <button onClick={toggleSidebar} className="sidebar-toggle">
            {showSidebar ? "Hide History" : "Show History"}
          </button>
          <button onClick={handleNewChat} className="new-chat-button">New Chat</button>
          <button onClick={handleAboutClick} className="about-button">About</button>
        </div>

        <div className="user-profile">
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
      </div>

      <div className={`app-content ${showSidebar ? 'with-sidebar' : ''}`}>
        {showSidebar && (
          <ChatHistorySidebar
            chatHistory={chatHistory}
            onSelectChat={selectChat}
            onDeleteChat={deleteChat}
            activeChat={activeChatId}
          />
        )}

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
    </div>
  );
};

export default App;
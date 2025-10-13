import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Backend API URL - adjust if backend runs on different port
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  // State management
  const [entrepreneurName, setEntrepreneurName] = useState('');
  const [businessIdea, setBusinessIdea] = useState({
    name: '',
    description: '',
    target_market: '',
    revenue_model: '',
    current_traction: '',
    investment_needed: '',
    use_of_funds: ''
  });

  const [judges, setJudges] = useState([
    {
      name: 'Mark Cuban',
      role: 'Shark Tank Judge',
      goal: 'Evaluate business pitches critically and decide whether to invest',
      backstory: `You are a successful entrepreneur and investor on Shark Tank.
You have a keen eye for promising businesses and can quickly identify flaws in business models.
You are tough but fair, and you always ask penetrating questions about revenue, margins,
customer acquisition costs, and scaling strategies. You're not afraid to say 'I'm out' if
the numbers don't add up or if you don't believe in the entrepreneur's ability to execute.`
    }
  ]);

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [pitchStarted, setPitchStarted] = useState(false);
  const [showSetup, setShowSetup] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);
  const [editingJudgeIndex, setEditingJudgeIndex] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Test API connection on mount
  useEffect(() => {
    testConnection();
  }, []);

  const testConnection = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/test-connection`);
      setApiConnected(true);
      console.log('API Connection successful:', response.data);
    } catch (error) {
      console.error('API Connection failed:', error);
      setApiConnected(false);
    }
  };

  // Handle business idea form changes
  const handleBusinessIdeaChange = (field, value) => {
    setBusinessIdea(prev => ({ ...prev, [field]: value }));
  };

  // Handle judge changes
  const handleJudgeChange = (index, field, value) => {
    const newJudges = [...judges];
    newJudges[index][field] = value;
    setJudges(newJudges);
  };

  // Add new judge
  const addJudge = () => {
    const newJudge = {
      name: '',
      role: 'Shark Tank Judge',
      goal: 'Evaluate business pitches critically and decide whether to invest',
      backstory: ''
    };
    setJudges([...judges, newJudge]);
    setEditingJudgeIndex(judges.length); // Auto-expand the new judge
  };

  // Remove judge
  const removeJudge = (index) => {
    if (judges.length > 1) {
      setJudges(judges.filter((_, i) => i !== index));
      if (editingJudgeIndex === index) {
        setEditingJudgeIndex(null);
      }
    }
  };

  // Toggle judge editing
  const toggleJudgeEdit = (index) => {
    setEditingJudgeIndex(editingJudgeIndex === index ? null : index);
  };

  // Start pitch
  const startPitch = async () => {
    if (!entrepreneurName.trim()) {
      alert('Please enter your name');
      return;
    }
    if (!businessIdea.name || !businessIdea.description) {
      alert('Please fill in at least the business name and description');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/start-pitch`, {
        business_idea: businessIdea,
        judges: judges,
        entrepreneur_name: entrepreneurName
      });

      setMessages(response.data.conversation_history);
      setPitchStarted(true);
      setShowSetup(false);
    } catch (error) {
      console.error('Error starting pitch:', error);
      alert('Failed to start pitch. Please check console for details.');
    } finally {
      setLoading(false);
    }
  };

  // Send message
  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      role: 'Entrepreneur',
      content: inputMessage,
      sender_name: entrepreneurName
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/send-message`, {
        content: inputMessage,
        sender: 'Entrepreneur'
      });

      setMessages(response.data.conversation_history);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please check console for details.');
    } finally {
      setLoading(false);
    }
  };

  // Reset conversation
  const resetConversation = async () => {
    if (window.confirm('Are you sure you want to start over?')) {
      try {
        await axios.post(`${API_URL}/api/reset`);
        setMessages([]);
        setPitchStarted(false);
        setShowSetup(true);
      } catch (error) {
        console.error('Error resetting conversation:', error);
      }
    }
  };

  // Load example business idea
  const loadExample = () => {
    // Only set name if it's empty, preserve existing name
    if (!entrepreneurName.trim()) {
      setEntrepreneurName('Alex Johnson');
    }
    setBusinessIdea({
      name: 'EcoTrack',
      description: 'A smart home energy management system that uses AI to optimize energy usage',
      target_market: 'Environmentally conscious homeowners and small businesses',
      revenue_model: 'Hardware sales + monthly subscription for premium features',
      current_traction: '500 beta users, $50,000 in pre-orders',
      investment_needed: '$300,000 for 10% equity',
      use_of_funds: 'Product refinement, marketing, and team expansion'
    });
  };

  // Get judge name from message
  const getJudgeName = (message) => {
    // Check if message has judge_name property
    if (message.judge_name) {
      return message.judge_name;
    }
    
    // Try to extract from content if it starts with "Name: "
    const content = message.content;
    const nameMatch = content.match(/^([^:]+):/);
    if (nameMatch) {
      const extractedName = nameMatch[1].trim();
      // Verify it's one of our judges
      const isJudge = judges.some(j => j.name.toLowerCase().includes(extractedName.toLowerCase()));
      if (isJudge) {
        return extractedName;
      }
    }
    
    // Default to first judge if no match found
    return judges[0]?.name || 'Judge';
  };

  // Get sender name for entrepreneur messages
  const getSenderName = (message) => {
    if (message.sender_name) {
      return message.sender_name;
    }
    return entrepreneurName || 'Entrepreneur';
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🦈 Shark Tank Pitch Simulator</h1>
          <p className="header-subtitle">Practice your pitch with AI-powered investors</p>
        </div>
        <div className="connection-badge">
          <div className={`status-indicator ${apiConnected ? 'connected' : 'disconnected'}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {apiConnected ? 'API Ready' : 'API Offline'}
            </span>
          </div>
        </div>
      </header>

      <div className="app-container">
        {showSetup ? (
          <div className="setup-panel">
            <div className="setup-header">
              <h2>Setup Your Pitch</h2>
              <p>Configure your business details and select your judges</p>
            </div>
            
            <div className="section">
              <div className="section-header">
                <h3>💼 Entrepreneur Information</h3>
              </div>
              
              <div className="form-group">
                <label>Your Name *</label>
                <input
                  type="text"
                  value={entrepreneurName}
                  onChange={(e) => setEntrepreneurName(e.target.value)}
                  placeholder="e.g., Alex Johnson"
                  className="input-field"
                />
                <span className="field-hint">This will appear in your messages</span>
              </div>
            </div>

            <div className="section">
              <div className="section-header">
                <h3>🚀 Business Idea</h3>
                <button onClick={loadExample} className="btn-link">
                  Load Example
                </button>
              </div>
              
              <div className="form-group">
                <label>Business Name *</label>
                <input
                  type="text"
                  value={businessIdea.name}
                  onChange={(e) => handleBusinessIdeaChange('name', e.target.value)}
                  placeholder="e.g., EcoTrack"
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label>Description *</label>
                <textarea
                  value={businessIdea.description}
                  onChange={(e) => handleBusinessIdeaChange('description', e.target.value)}
                  placeholder="What does your business do?"
                  rows="3"
                  className="textarea-field"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Target Market</label>
                  <input
                    type="text"
                    value={businessIdea.target_market}
                    onChange={(e) => handleBusinessIdeaChange('target_market', e.target.value)}
                    placeholder="Who are your customers?"
                    className="input-field"
                  />
                </div>

                <div className="form-group">
                  <label>Revenue Model</label>
                  <input
                    type="text"
                    value={businessIdea.revenue_model}
                    onChange={(e) => handleBusinessIdeaChange('revenue_model', e.target.value)}
                    placeholder="How do you make money?"
                    className="input-field"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Current Traction</label>
                  <input
                    type="text"
                    value={businessIdea.current_traction}
                    onChange={(e) => handleBusinessIdeaChange('current_traction', e.target.value)}
                    placeholder="Users, revenue, growth metrics"
                    className="input-field"
                  />
                </div>

                <div className="form-group">
                  <label>Investment Needed</label>
                  <input
                    type="text"
                    value={businessIdea.investment_needed}
                    onChange={(e) => handleBusinessIdeaChange('investment_needed', e.target.value)}
                    placeholder="e.g., $300,000 for 10% equity"
                    className="input-field"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Use of Funds</label>
                <textarea
                  value={businessIdea.use_of_funds}
                  onChange={(e) => handleBusinessIdeaChange('use_of_funds', e.target.value)}
                  placeholder="How will you use the investment?"
                  rows="2"
                  className="textarea-field"
                />
              </div>
            </div>

            <div className="section">
              <div className="section-header">
                <h3>👔 Judges Panel ({judges.length})</h3>
                <button onClick={addJudge} className="btn-add-judge">
                  <span className="btn-icon">+</span> Add Judge
                </button>
              </div>

              <div className="judges-list">
                {judges.map((judge, index) => (
                  <div key={index} className={`judge-card ${editingJudgeIndex === index ? 'editing' : ''}`}>
                    <div className="judge-card-header" onClick={() => toggleJudgeEdit(index)}>
                      <div className="judge-info">
                        <div className="judge-avatar">
                          {judge.name ? judge.name.charAt(0).toUpperCase() : '?'}
                        </div>
                        <div className="judge-details">
                          <h4>{judge.name || `Judge ${index + 1} (Click to edit)`}</h4>
                          <span className="judge-status">
                            {judge.name && judge.backstory ? '✓ Configured' : '⚠ Incomplete'}
                          </span>
                        </div>
                      </div>
                      <div className="judge-actions">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleJudgeEdit(index);
                          }}
                          className="btn-icon-small"
                          title="Edit judge"
                        >
                          ✏️
                        </button>
                        {judges.length > 1 && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              removeJudge(index);
                            }}
                            className="btn-icon-small btn-danger"
                            title="Remove judge"
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    </div>

                    {editingJudgeIndex === index && (
                      <div className="judge-card-body">
                        <div className="form-group">
                          <label>Judge Name *</label>
                          <input
                            type="text"
                            value={judge.name}
                            onChange={(e) => handleJudgeChange(index, 'name', e.target.value)}
                            placeholder="e.g., Mark Cuban"
                            className="input-field"
                          />
                        </div>

                        <div className="form-group">
                          <label>Personality & Investment Style *</label>
                          <textarea
                            value={judge.backstory}
                            onChange={(e) => handleJudgeChange(index, 'backstory', e.target.value)}
                            placeholder="Describe the judge's personality, expertise, and investment criteria..."
                            rows="5"
                            className="textarea-field"
                          />
                          <span className="field-hint">
                            This defines how the judge will evaluate your pitch
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="info-section">
              <h3>📋 How to Structure Your Pitch</h3>
              <div className="info-grid">
                <div className="info-item">
                  <strong>Name:</strong> Clear, memorable name
                </div>
                <div className="info-item">
                  <strong>Description:</strong> Problem + Solution
                </div>
                <div className="info-item">
                  <strong>Target Market:</strong> Customer segments & market size
                </div>
                <div className="info-item">
                  <strong>Revenue Model:</strong> How you make money
                </div>
                <div className="info-item">
                  <strong>Current Traction:</strong> Users, revenue, growth
                </div>
                <div className="info-item">
                  <strong>Investment:</strong> Amount & equity offered
                </div>
              </div>
            </div>

            <button
              onClick={startPitch}
              disabled={loading || !apiConnected || !entrepreneurName.trim()}
              className="btn-primary btn-large"
            >
              {loading ? (
                <>
                  <span className="spinner"></span> Starting Pitch...
                </>
              ) : (
                <>
                  🎤 Start Pitch Session
                </>
              )}
            </button>
          </div>
        ) : (
          <div className="chat-layout">
            <div className="chat-panel">
              <div className="chat-header">
                <div>
                  <h2>Live Pitch Session</h2>
                  <p className="chat-subtitle">Pitching to {judges.length} judge{judges.length > 1 ? 's' : ''}</p>
                </div>
                <button onClick={resetConversation} className="btn-secondary">
                  ↻ Start Over
                </button>
              </div>

              <div className="messages-container">
                {messages.map((msg, index) => {
                  const isEntrepreneur = msg.role === 'Entrepreneur';
                  const displayName = isEntrepreneur ? getSenderName(msg) : getJudgeName(msg);
                  const avatarInitial = displayName.charAt(0).toUpperCase();
                  
                  return (
                    <div
                      key={index}
                      className={`message ${msg.role.toLowerCase()}`}
                    >
                      <div className="message-avatar">
                        {isEntrepreneur ? (
                          <div className="avatar entrepreneur-avatar">
                            {avatarInitial}
                          </div>
                        ) : (
                          <div className="avatar judge-avatar">
                            {avatarInitial}
                          </div>
                        )}
                      </div>
                      <div className="message-bubble">
                        <div className="message-header">
                          <span className="message-sender">
                            {displayName}
                          </span>
                          <span className="message-role">
                            {msg.role}
                          </span>
                        </div>
                        <div className="message-content">{msg.content}</div>
                      </div>
                    </div>
                  );
                })}
                {loading && (
                  <div className="message judge">
                    <div className="message-avatar">
                      <div className="avatar judge-avatar">J</div>
                    </div>
                    <div className="message-bubble">
                      <div className="message-header">
                        <span className="message-sender">Judge</span>
                        <span className="message-role">Thinking...</span>
                      </div>
                      <div className="message-content typing">
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="input-container">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
                  placeholder="Type your response to the judge..."
                  disabled={loading}
                  className="message-input"
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !inputMessage.trim()}
                  className="btn-send"
                >
                  {loading ? '⏳' : '📤'} Send
                </button>
              </div>
            </div>

            <div className="judges-sidebar">
              <h3>Judges Panel</h3>
              {judges.map((judge, index) => (
                <div key={index} className="sidebar-judge-card">
                  <div className="sidebar-judge-avatar">
                    {judge.name ? judge.name.charAt(0).toUpperCase() : '?'}
                  </div>
                  <div className="sidebar-judge-info">
                    <h4>{judge.name || `Judge ${index + 1}`}</h4>
                    <p className="sidebar-judge-role">Investor</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
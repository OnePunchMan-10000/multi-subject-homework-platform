import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BookOpen, FileText, Upload, Send, Brain, Map, HelpCircle, CheckCircle } from 'lucide-react';
import MermaidDiagram from './components/MermaidDiagram';
import Quiz from './components/Quiz';
import FormattedAnswer from './components/FormattedAnswer';
import PedagogicalTabs from './components/PedagogicalTabs';

function App() {
  const [activeTab, setActiveTab] = useState('question');
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [question, setQuestion] = useState('');
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await axios.get('/api/subjects');
      setSubjects(response.data);
      setSelectedSubject(response.data.find(s => s.active));
    } catch (error) {
      console.error('Error fetching subjects:', error);
    }
  };

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('/api/ask', {
        question,
        subject: selectedSubject?.name
      });
      setResults(response.data);
    } catch (error) {
      console.error('Error submitting question:', error);
      alert('Error processing your question. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePdfSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || !pdfFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('question', question);
    formData.append('pdf', pdfFile);

    try {
      const response = await axios.post('/api/ask-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResults(response.data);
    } catch (error) {
      console.error('Error submitting PDF question:', error);
      alert('Error processing your PDF question. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setPdfFile(file);
    } else {
      alert('Please select a valid PDF file.');
      e.target.value = '';
    }
  };

  const handleExampleQuestion = () => {
    setQuestion('explain total internal reflection');
    setActiveTab('question');
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🎓 Educational Q&A Platform</h1>
        <p>AI-powered learning with interactive pedagogical tools</p>
      </header>

      <div className="main-card">
        {/* Subjects Bar */}
        <div className="subjects-bar">
          {subjects.map(subject => (
            <div
              key={subject.id}
              className={`subject-chip ${subject.active ? 'active' : 'inactive'}`}
              onClick={() => subject.active && setSelectedSubject(subject)}
            >
              {subject.name}
              {!subject.active && ' (Coming Soon)'}
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'question' ? 'active' : ''}`}
            onClick={() => setActiveTab('question')}
          >
            <BookOpen size={18} />
            Ask Question
          </button>
          <button
            className={`tab ${activeTab === 'pdf' ? 'active' : ''}`}
            onClick={() => setActiveTab('pdf')}
          >
            <FileText size={18} />
            PDF Analysis
          </button>
        </div>

        {/* Question Tab */}
        {activeTab === 'question' && (
          <form onSubmit={handleQuestionSubmit}>
            <div className="input-section">
              <label htmlFor="question">
                <BookOpen size={18} />
                Your Question
              </label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask any question related to your subject..."
                required
              />
              <small style={{ color: '#666', fontSize: '0.9rem' }}>
                💡 Try the example: 
                <button 
                  type="button" 
                  onClick={handleExampleQuestion}
                  style={{ 
                    background: 'none', 
                    border: 'none', 
                    color: '#667eea', 
                    cursor: 'pointer',
                    textDecoration: 'underline',
                    marginLeft: '5px'
                  }}
                >
                  "explain total internal reflection"
                </button>
              </small>
            </div>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? (
                <>Processing... ⏳</>
              ) : (
                <>
                  <Send size={18} />
                  Get AI-Powered Answer
                </>
              )}
            </button>
          </form>
        )}

        {/* PDF Tab */}
        {activeTab === 'pdf' && (
          <form onSubmit={handlePdfSubmit}>
            <div className="input-section">
              <label htmlFor="pdf-question">
                <FileText size={18} />
                Your Question
              </label>
              <textarea
                id="pdf-question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about your uploaded PDF..."
                required
              />
            </div>
            
            <div className="file-upload">
              <label htmlFor="pdf-file">
                <Upload size={18} />
                Upload PDF Document
              </label>
              <input
                type="file"
                id="pdf-file"
                accept=".pdf"
                onChange={handleFileChange}
                required
              />
              {pdfFile && (
                <p style={{ marginTop: '10px', color: '#667eea' }}>
                  ✓ Selected: {pdfFile.name}
                </p>
              )}
            </div>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? (
                <>Analyzing PDF... ⏳</>
              ) : (
                <>
                  <Send size={18} />
                  Analyze PDF & Answer
                </>
              )}
            </button>
          </form>
        )}

        {/* Loading */}
        {loading && (
          <div className="loading">
            <p>🤖 AI is working on your question...</p>
            <p>Generating answer...</p>
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <div className="results">
            {results.answer && (
              <FormattedAnswer answer={results.answer} />
            )}

            {results.context && (
              <div className="answer-section" style={{
                background: 'linear-gradient(135deg, #fff3cd, #ffffff)',
                padding: '25px',
                borderRadius: '12px',
                marginBottom: '20px',
                border: '1px solid #ffeaa7',
                boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
              }}>
                <h3 style={{
                  color: '#856404',
                  marginBottom: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  fontSize: '1.2rem',
                  fontWeight: 'bold'
                }}>
                  <FileText size={20} />
                  📄 Relevant Context from PDF
                </h3>
                <div style={{
                  background: '#ffffff',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '1px solid #f4e5d3',
                  fontSize: '0.95rem',
                  lineHeight: '1.6',
                  color: '#333'
                }}>
                  <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontFamily: 'inherit' }}>
                    {results.context}
                  </pre>
                </div>
              </div>
            )}

            {results.pedagogical && (
              (results.pedagogical.flowchart || results.pedagogical.flowsteps || results.pedagogical.mindmap || results.pedagogical.quiz) && (
                <PedagogicalTabs 
                  pedagogical={{ ...(results.pedagogical || {}), question: question }} 
                />
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
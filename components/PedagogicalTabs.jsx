import React, { useState, useEffect } from 'react';
import { Map, Brain, HelpCircle, List, BookOpen, Target } from 'lucide-react';
import MermaidDiagram from './MermaidDiagram';
import Quiz from './Quiz';

const PedagogicalTabs = ({ pedagogical }) => {
  const [activeTab, setActiveTab] = useState('flowchart');
  
  // Function to extract detailed steps from flowchart content
  const extractFlowSteps = (flowchartContent) => {
    if (!flowchartContent || typeof flowchartContent !== 'string') return [];
    
    const steps = [];
    const lines = flowchartContent.split('\n');
    let stepCounter = 1;
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      
      // Skip graph declarations and empty lines
      if (trimmedLine.startsWith('graph ') || 
          trimmedLine.startsWith('flowchart ') || 
          trimmedLine === '' ||
          trimmedLine.includes('-->') ||
          trimmedLine.includes('---') ||
          trimmedLine.includes('==>'))
        continue;
        
      // Extract content from flowchart nodes
      const nodeMatch = trimmedLine.match(/\w+\[(.*?)\]|\w+\((.*?)\)|\w+\{(.*?)\}|(\w+)>.*\]/);
      if (nodeMatch) {
        const content = nodeMatch[1] || nodeMatch[2] || nodeMatch[3] || nodeMatch[4];
        if (content && content.length > 5) { // Lower threshold for content
          steps.push({
            step: stepCounter++,
            content: content.replace(/"/g, '').trim()
          });
        }
      }
    }
    
    return steps;
  };
  
  // Function to extract detailed steps from flowchart content or use generated flowsteps
  const getFlowSteps = () => {
    // If we have generated flowsteps, parse them
    if (pedagogical.flowsteps && typeof pedagogical.flowsteps === 'string') {
      const steps = [];
      const lines = pedagogical.flowsteps.split('\n');
      let stepCounter = 1;
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        
        // Skip empty lines
        if (!trimmedLine) continue;
        
        // Look for numbered steps or bullet points
        const stepMatch = trimmedLine.match(/^(\d+\.?|\-|\*|\u2022)\s*(.+)$/);
        if (stepMatch && stepMatch[2].length > 10) {
          steps.push({
            step: stepCounter++,
            content: stepMatch[2].trim()
          });
        } else if (trimmedLine.length > 10 && !trimmedLine.includes(':')) {
          // Include substantial lines that don't look like headers
          steps.push({
            step: stepCounter++,
            content: trimmedLine
          });
        }
      }
      
      return steps;
    }
    
    // Fallback: extract from flowchart if no flowsteps available
    if (pedagogical.flowchart && typeof pedagogical.flowchart === 'string') {
      return extractFlowSteps(pedagogical.flowchart);
    }
    
    return [];
  };
  
  const flowSteps = getFlowSteps();
  
  // Check if content is available for each tab
  const hasFlowchart = pedagogical.flowchart && typeof pedagogical.flowchart === 'string' && pedagogical.flowchart.length > 50;
  const hasFlowSteps = flowSteps && flowSteps.length > 0;
  const hasMindMap = pedagogical.mindmap && typeof pedagogical.mindmap === 'string' && pedagogical.mindmap.length > 50;
  const hasQuiz = pedagogical.quiz && pedagogical.quiz.questions && Array.isArray(pedagogical.quiz.questions) && pedagogical.quiz.questions.length > 0;

  const tabs = [
    {
      id: 'flowchart',
      name: 'Visual Flowchart',
      icon: Map,
      content: hasFlowchart ? pedagogical.flowchart : null,
      available: hasFlowchart
    },
    {
      id: 'flowsteps',
      name: 'Flow Steps',
      icon: List,
      content: hasFlowSteps ? flowSteps : null,
      available: hasFlowSteps
    },
    {
      id: 'mindmap',
      name: 'Mind Map',
      icon: Brain,
      content: hasMindMap ? pedagogical.mindmap : null,
      available: hasMindMap
    },
    {
      id: 'quiz',
      name: 'Knowledge Quiz',
      icon: HelpCircle,
      content: hasQuiz ? pedagogical.quiz : null,
      available: hasQuiz
    }
  ];

  // Set the first available tab as active if current active tab is not available
  const availableTabs = tabs.filter(tab => tab.available);
  const firstAvailableTab = availableTabs.length > 0 ? availableTabs[0].id : 'flowchart';
  
  // If the current active tab is not available, switch to the first available one
  useEffect(() => {
    if (!tabs.find(tab => tab.id === activeTab && tab.available)) {
      setActiveTab(firstAvailableTab);
    }
  }, [pedagogical, activeTab, firstAvailableTab]);

  return (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '30px',
      marginTop: '30px',
      boxShadow: '0 6px 25px rgba(0,0,0,0.1)',
      border: '1px solid #e1e5e9'
    }}>
      {/* Header */}
      <div style={{
        textAlign: 'center',
        marginBottom: '30px'
      }}>
        <h3 style={{
          color: '#333',
          fontSize: '1.5rem',
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          marginBottom: '15px'
        }}>
          <BookOpen size={24} color="#667eea" />
          Interactive Learning Tools
        </h3>
        <p style={{
          color: '#666',
          fontSize: '1.1rem',
          maxWidth: '700px',
          margin: '0 auto',
          lineHeight: '1.7'
        }}>
          Enhance your understanding with these interactive educational tools designed to reinforce key concepts
        </p>
      </div>

      {/* Tab Navigation */}
      <div style={{
        display: 'flex',
        borderBottom: '3px solid #f0f0f0',
        marginBottom: '35px',
        justifyContent: 'center',
        flexWrap: 'wrap',
        gap: '15px'
      }}>
        {tabs.map((tab) => {
          const IconComponent = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '18px 30px',
                border: 'none',
                background: 'none',
                cursor: 'pointer',
                fontSize: '1.1rem',
                fontWeight: '600',
                color: activeTab === tab.id ? '#667eea' : '#666',
                borderBottom: `3px solid ${activeTab === tab.id ? '#667eea' : 'transparent'}`,
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                minWidth: '200px',
                justifyContent: 'center',
                borderRadius: '10px 10px 0 0',
                transform: activeTab === tab.id ? 'translateY(-3px)' : 'none',
                boxShadow: activeTab === tab.id ? '0 -3px 15px rgba(102, 126, 234, 0.15)' : 'none',
                backgroundColor: activeTab === tab.id ? 'rgba(102, 126, 234, 0.05)' : 'transparent'
              }}
              disabled={!tab.available}
            >
              <IconComponent size={20} />
              <span>{tab.name}</span>
              {!tab.available && <span style={{ fontSize: '0.8rem', color: '#999' }}> (Generating...)</span>}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div style={{
        minHeight: '450px',
        background: '#fafbfc',
        borderRadius: '15px',
        padding: '30px',
        border: '1px solid #e8eaed',
        boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.05)'
      }}>
        {activeTab === 'flowchart' && (
          <div>
            <div style={{
              marginBottom: '25px',
              textAlign: 'center'
            }}>
              <h4 style={{
                color: '#667eea',
                fontSize: '1.3rem',
                fontWeight: 'bold',
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px'
              }}>
                <Map size={22} />
                Visual Process Flow
              </h4>
              <p style={{
                color: '#666',
                fontSize: '1rem',
                maxWidth: '650px',
                margin: '0 auto',
                lineHeight: '1.7'
              }}>
                Visual diagram showing the process flow. For detailed step-by-step explanations, please check the "Flow Steps" tab.
              </p>
            </div>
            {hasFlowchart ? (
              <MermaidDiagram 
                type="flowchart" 
                topic={pedagogical.question || pedagogical.topic || 'Physics'} 
                subject={pedagogical.subject || 'Physics'} 
                chart={pedagogical.flowchart} 
              />
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '50px',
                color: '#666',
                background: 'white',
                borderRadius: '12px',
                border: '2px dashed #e1e5e9'
              }}>
                <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🔄</div>
                <h4 style={{ margin: '0 0 15px', color: '#667eea' }}>Generating Flowchart</h4>
                <p>Our AI is creating a visual flowchart to help you understand this concept better. Please try your question again in a moment.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'flowsteps' && (
          <div>
            <div style={{
              marginBottom: '25px',
              textAlign: 'center'
            }}>
              <h4 style={{
                color: '#667eea',
                fontSize: '1.3rem',
                fontWeight: 'bold',
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px'
              }}>
                <List size={22} />
                Detailed Flow Steps
              </h4>
              <p style={{
                color: '#666',
                fontSize: '1rem',
                maxWidth: '650px',
                margin: '0 auto',
                lineHeight: '1.7'
              }}>
                Step-by-step breakdown with detailed explanations, formulas, and practical examples
              </p>
            </div>
            
            {hasFlowSteps ? (
              <div style={{
                maxWidth: '850px',
                margin: '0 auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '25px'
              }}>
                {flowSteps.map((step, index) => (
                  <div key={index} style={{
                    background: 'white',
                    border: '2px solid #667eea',
                    borderRadius: '15px',
                    padding: '25px',
                    boxShadow: '0 6px 15px rgba(102, 126, 234, 0.2)',
                    position: 'relative',
                    transition: 'transform 0.3s ease, box-shadow 0.3s ease'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-5px)';
                    e.currentTarget.style.boxShadow = '0 10px 25px rgba(102, 126, 234, 0.3)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 6px 15px rgba(102, 126, 234, 0.2)';
                  }}
                  >
                    <div style={{
                      position: 'absolute',
                      top: '-15px',
                      left: '25px',
                      background: '#667eea',
                      color: 'white',
                      padding: '6px 15px',
                      borderRadius: '25px',
                      fontSize: '1rem',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <Target size={16} />
                      Step {step.step}
                    </div>
                    <div style={{
                      fontSize: '1.05rem',
                      lineHeight: '1.7',
                      color: '#333',
                      marginTop: '15px'
                    }}>
                      {step.content}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{
                textAlign: 'center',
                color: '#666',
                fontSize: '1.1rem',
                padding: '50px',
                background: 'white',
                borderRadius: '12px',
                border: '2px dashed #e1e5e9'
              }}>
                <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🔄</div>
                <h4 style={{ margin: '0 0 15px', color: '#667eea' }}>Generating Step-by-Step Guide</h4>
                <p>Our AI is creating detailed step-by-step explanations to help you understand this concept better. Please try your question again in a moment.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'mindmap' && (
          <div>
            <div style={{
              marginBottom: '25px',
              textAlign: 'center'
            }}>
              <h4 style={{
                color: '#667eea',
                fontSize: '1.3rem',
                fontWeight: 'bold',
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px'
              }}>
                <Brain size={22} />
                Concept Relationships
              </h4>
              <p style={{
                color: '#666',
                fontSize: '1rem',
                maxWidth: '650px',
                margin: '0 auto',
                lineHeight: '1.7'
              }}>
                Explore how different concepts connect and relate to each other in a hierarchical structure
              </p>
            </div>
            {hasMindMap ? (
              <MermaidDiagram 
                type="mindmap" 
                topic={pedagogical.question || pedagogical.topic || 'Physics'} 
                subject={pedagogical.subject || 'Physics'} 
                chart={pedagogical.mindmap} 
              />
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '50px',
                color: '#666',
                background: 'white',
                borderRadius: '12px',
                border: '2px dashed #e1e5e9'
              }}>
                <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🔄</div>
                <h4 style={{ margin: '0 0 15px', color: '#667eea' }}>Generating Mind Map</h4>
                <p>Our AI is creating a mind map to help you visualize the relationships between concepts. Please try your question again in a moment.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'quiz' && (
          <div>
            <div style={{
              marginBottom: '25px',
              textAlign: 'center'
            }}>
              <h4 style={{
                color: '#667eea',
                fontSize: '1.3rem',
                fontWeight: 'bold',
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px'
              }}>
                <HelpCircle size={22} />
                Knowledge Quiz
              </h4>
              <p style={{
                color: '#666',
                fontSize: '1rem',
                maxWidth: '650px',
                margin: '0 auto',
                lineHeight: '1.7'
              }}>
                Challenge yourself with these questions to reinforce your understanding and identify areas for improvement
              </p>
            </div>
            {hasQuiz ? (
              <Quiz quiz={pedagogical.quiz} />
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '50px',
                color: '#666',
                background: 'white',
                borderRadius: '12px',
                border: '2px dashed #e1e5e9'
              }}>
                <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🔄</div>
                <h4 style={{ margin: '0 0 15px', color: '#667eea' }}>Generating Quiz</h4>
                <p>Our AI is creating a quiz to test your understanding of this concept. Please try your question again in a moment.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Educational Message */}
      <div style={{
        marginTop: '25px',
        textAlign: 'center',
        padding: '20px',
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        borderRadius: '12px',
        color: 'white'
      }}>
        <p style={{ 
          margin: 0, 
          fontSize: '1.1rem',
          fontWeight: '500',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px'
        }}>
          <BookOpen size={20} />
          These interactive tools are designed to enhance your learning experience and deepen your understanding
        </p>
      </div>

      {/* Progress Indicator */}
      <div style={{
        marginTop: '25px',
        textAlign: 'center',
        display: 'flex',
        justifyContent: 'center',
        gap: '12px'
      }}>
        {tabs.map((tab, index) => (
          <div
            key={tab.id}
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: activeTab === tab.id ? '#667eea' : '#e1e5e9',
              transition: 'background 0.3s ease',
              boxShadow: activeTab === tab.id ? '0 0 8px rgba(102, 126, 234, 0.5)' : 'none'
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default PedagogicalTabs;
import React from 'react';

const VisualDiagram = ({ type, chart, title }) => {
  if (!chart) return null;

  // Parse the chart content to extract meaningful information
  const parseChartContent = (chartText) => {
    const lines = chartText.split('\n').filter(line => line.trim());
    const nodes = [];
    const connections = [];
    
    lines.forEach(line => {
      line = line.trim();
      
      // Extract nodes and connections
      if (line.includes('-->') || line.includes('---')) {
        const parts = line.split(/-->|---/);
        if (parts.length >= 2) {
          const from = parts[0].trim().replace(/[A-Z]\[|\]/g, '');
          const to = parts[1].trim().replace(/[A-Z]\[|\]/g, '');
          connections.push({ from, to });
        }
      }
      
      // Extract node definitions
      const nodeMatch = line.match(/([A-Z]+)\[(.*?)\]/);
      if (nodeMatch) {
        nodes.push({
          id: nodeMatch[1],
          label: nodeMatch[2].replace(/"/g, '')
        });
      }
      
      // Extract mindmap nodes
      if (line.includes('((') || line.includes('))')) {
        const mindmapMatch = line.match(/\(\((.*?)\)\)/);
        if (mindmapMatch) {
          nodes.push({
            id: 'root',
            label: mindmapMatch[1],
            isRoot: true
          });
        }
      }
    });
    
    return { nodes, connections };
  };

  const { nodes, connections } = parseChartContent(chart);
  
  if (type === 'flowchart') {
    return (
      <div style={{
        fontFamily: 'Segoe UI, sans-serif',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '30px',
        borderRadius: '12px',
        color: 'white',
        minHeight: '300px'
      }}>
        <h3 style={{ 
          textAlign: 'center', 
          marginBottom: '25px',
          fontSize: '1.2rem',
          fontWeight: 'bold'
        }}>
          📊 {title || 'Process Flowchart'}
        </h3>
        
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '15px'
        }}>
          {nodes.map((node, index) => (
            <div key={index} style={{
              background: 'rgba(255,255,255,0.9)',
              color: '#333',
              padding: '15px 20px',
              borderRadius: '8px',
              margin: '0 auto',
              maxWidth: '80%',
              textAlign: 'center',
              fontWeight: '500',
              boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
              position: 'relative'
            }}>
              <div style={{
                fontSize: '0.9rem',
                opacity: 0.7,
                marginBottom: '5px'
              }}>
                Step {index + 1}
              </div>
              {node.label}
              {index < nodes.length - 1 && (
                <div style={{
                  position: 'absolute',
                  bottom: '-12px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  fontSize: '20px',
                  color: 'white'
                }}>
                  ↓
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div style={{
          textAlign: 'center',
          marginTop: '20px',
          fontSize: '0.85rem',
          opacity: 0.8
        }}>
          Visual representation of the educational process flow
        </div>
      </div>
    );
  }
  
  if (type === 'mindmap') {
    return (
      <div style={{
        fontFamily: 'Segoe UI, sans-serif',
        background: 'linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%)',
        padding: '30px',
        borderRadius: '12px',
        color: 'white',
        minHeight: '300px'
      }}>
        <h3 style={{ 
          textAlign: 'center', 
          marginBottom: '25px',
          fontSize: '1.2rem',
          fontWeight: 'bold'
        }}>
          🧠 {title || 'Concept Mind Map'}
        </h3>
        
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '15px',
          alignItems: 'center'
        }}>
          {nodes.map((node, index) => (
            <div key={index} style={{
              background: node.isRoot ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.8)',
              color: '#333',
              padding: node.isRoot ? '20px 25px' : '12px 18px',
              borderRadius: '50px',
              fontSize: node.isRoot ? '1.1rem' : '0.9rem',
              fontWeight: node.isRoot ? 'bold' : '500',
              textAlign: 'center',
              boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
              border: node.isRoot ? '3px solid #fff' : '2px solid rgba(255,255,255,0.5)',
              minWidth: node.isRoot ? '150px' : '100px',
              transform: node.isRoot ? 'scale(1.1)' : 'scale(1)'
            }}>
              {node.label}
            </div>
          ))}
        </div>
        
        <div style={{
          textAlign: 'center',
          marginTop: '20px',
          fontSize: '0.85rem',
          opacity: 0.8
        }}>
          Interactive concept relationship visualization
        </div>
      </div>
    );
  }
  
  return null;
};

export default VisualDiagram;
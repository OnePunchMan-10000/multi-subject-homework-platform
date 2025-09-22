import React from 'react';
import { Brain, Lightbulb, BookOpen, Target, Zap } from 'lucide-react';

const FormattedAnswer = ({ answer }) => {
  const formatAnswer = (text) => {
    if (!text) return '';

    // Lightweight LaTeX -> plain text substitutions for simple formulas (original behavior)
    const latexSimplify = (s) => {
      if (!s) return s;
      s = s.replace(/\\text\{([^}]*)\}/g, '$1');
      s = s.replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, '($1)/($2)');
      s = s.replace(/\$(.*?)\$/g, '$1').replace(/\\\((.*?)\\\)/g, '$1').replace(/\$\$(.*?)\$\$/g, '$1');
      return s;
    };

    // Clean the text from markdown symbols (no HTML injection)
    let cleanText = latexSimplify(text)
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/#{1,6}\s*/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .trim();
    
    const lines = cleanText.split('\n').filter(line => line.trim());
    const formattedContent = [];
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim();
      
      // Skip empty lines
      if (!trimmedLine) return;
      
      // Main headings - look for specific patterns and standalone titles
      if (
        trimmedLine.match(/^(Total Internal Reflection|Key Conditions?|Critical Angle|Formula|Formula for Critical Angle|Applications of TIR|Real-world Applications?|Applications?|Conditions?|Principles?|Examples?|Definition|Explanation|Important|Note|Overview|Summary|Introduction|Conclusion|Memory Aids?|Practice Tips?|Historical Context|Visual Descriptions?)s?:?$/i) ||
        (trimmedLine.length < 60 && trimmedLine.match(/^[A-Z][A-Za-z\s]+:?$/) && !trimmedLine.includes('.') && !trimmedLine.includes('('))
      ) {
        // Determine which icon to use based on heading content
        let icon = <BookOpen size={20} />;
        if (trimmedLine.toLowerCase().includes('formula') || trimmedLine.toLowerCase().includes('math')) {
          icon = <Target size={20} />;
        } else if (trimmedLine.toLowerCase().includes('tip') || trimmedLine.toLowerCase().includes('aid') || trimmedLine.toLowerCase().includes('memory')) {
          icon = <Lightbulb size={20} />;
        } else if (trimmedLine.toLowerCase().includes('example') || trimmedLine.toLowerCase().includes('application')) {
          icon = <Zap size={20} />;
        }
        
        formattedContent.push(
          <h2 key={index} style={{
            color: '#667eea',
            fontWeight: 'bold',
            fontSize: '1.5rem',
            marginTop: index === 0 ? '0' : '30px',
            marginBottom: '20px',
            borderBottom: '3px solid #667eea',
            paddingBottom: '12px',
            textTransform: 'capitalize',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            {icon}
            <span>{trimmedLine.replace(/:$/, '')}</span>
          </h2>
        );
      }
      // Numbered lists
      else if (trimmedLine.match(/^\d+\./)) {
        formattedContent.push(
          <div key={index} style={{
            marginLeft: '25px',
            marginBottom: '15px',
            lineHeight: '1.9',
            display: 'flex',
            alignItems: 'flex-start'
          }}>
            <span style={{ 
              color: '#667eea', 
              fontWeight: 'bold',
              minWidth: '35px',
              fontSize: '1.2rem',
              background: 'rgba(102, 126, 234, 0.1)',
              borderRadius: '50%',
              height: '35px',
              width: '35px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '15px'
            }}>
              {trimmedLine.match(/^\d+\./)[0].replace('.', '')}
            </span>
            <span style={{ flex: 1, fontSize: '1.05rem', paddingTop: '5px' }}>
              {trimmedLine.replace(/^\d+\.\s*/, '')}
            </span>
          </div>
        );
      }
      // Bullet points
      else if (trimmedLine.match(/^[-•]\s/)) {
        formattedContent.push(
          <div key={index} style={{
            marginLeft: '30px',
            marginBottom: '12px',
            lineHeight: '1.8',
            display: 'flex',
            alignItems: 'flex-start'
          }}>
            <span style={{ 
              color: '#667eea', 
              marginRight: '15px', 
              fontWeight: 'bold',
              fontSize: '1.3rem'
            }}>
              •
            </span>
            <span style={{ flex: 1, fontSize: '1.05rem' }}>
              {trimmedLine.replace(/^[-•]\s*/, '')}
            </span>
          </div>
        );
      }
      // Formula or technical content
      else if (trimmedLine.match(/[=<>≤≥θπ∞√∑∆]/) || trimmedLine.toLowerCase().includes('formula')) {
        formattedContent.push(
          <div key={index} style={{
            background: 'linear-gradient(135deg, #f8f9fa, #e9ecef)',
            border: '2px solid #667eea',
            borderRadius: '12px',
            padding: '20px',
            margin: '20px 0',
            fontFamily: 'monospace',
            fontSize: '1.15rem',
            color: '#495057',
            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.15)',
            position: 'relative'
          }}>
            <div style={{ 
              color: '#667eea', 
              fontWeight: 'bold', 
              marginBottom: '10px',
              fontFamily: 'inherit',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Target size={20} />
              <span>Formula & Calculation:</span>
            </div>
            {trimmedLine}
          </div>
        );
      }
      // Sub-headings - shorter descriptive lines that end with colon
      else if (trimmedLine.length < 100 && trimmedLine.includes(':') && trimmedLine.match(/^[A-Z]/)) {
        const [title, content] = trimmedLine.split(':');
        formattedContent.push(
          <div key={index} style={{ marginBottom: '18px' }}>
            <h3 style={{
              color: '#495057',
              fontWeight: '700',
              fontSize: '1.2rem',
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}>
              <span style={{ color: '#667eea' }}>▶</span>
              {title.trim()}
            </h3>
            {content && (
              <p style={{ lineHeight: '1.8', color: '#333', marginLeft: '25px', fontSize: '1.05rem' }}>
                {content.trim()}
              </p>
            )}
          </div>
        );
      }
      // Regular paragraphs
      else {
        formattedContent.push(
          <p key={index} style={{
            lineHeight: '1.9',
            marginBottom: '20px',
            color: '#333',
            textAlign: 'justify',
            fontSize: '1.05rem',
            fontWeight: '400'
          }}>
            {trimmedLine}
          </p>
        );
      }
    });
    
    return formattedContent;
  };

  return (
    <div className="answer-section" style={{
      background: 'linear-gradient(135deg, #f8f9fa, #ffffff)',
      padding: '30px',
      borderRadius: '15px',
      marginBottom: '25px',
      border: '1px solid #e1e5e9',
      boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
    }}>
      <h3 style={{
        color: '#667eea',
        marginBottom: '25px',
        display: 'flex',
        alignItems: 'center',
        gap: '15px',
        fontSize: '1.4rem',
        fontWeight: 'bold'
      }}>
        <Brain size={24} />
        AI-Powered Educational Answer
      </h3>
      <div style={{
        fontSize: '1.05rem',
        lineHeight: '1.7'
      }}>
        {formatAnswer(answer)}
      </div>
      
      <div style={{
        marginTop: '30px',
        padding: '20px',
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        borderRadius: '12px',
        color: 'white',
        textAlign: 'center'
      }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          gap: '10px',
          marginBottom: '10px'
        }}>
          <Lightbulb size={22} />
          <h4 style={{ margin: 0, fontSize: '1.2rem' }}>Learning Tip</h4>
        </div>
        <p style={{ margin: '10px 0 0', fontSize: '1rem', lineHeight: '1.6' }}>
          Review the interactive tools below to reinforce your understanding of this concept!
        </p>
      </div>
    </div>
  );
};

export default FormattedAnswer;
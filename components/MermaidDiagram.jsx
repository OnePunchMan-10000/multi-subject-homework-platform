import React, { useEffect, useRef, useState } from 'react';
import VisualDiagram from './VisualDiagram';

const MermaidDiagram = ({ type, topic, subject, chart }) => {
  const containerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFallback, setShowFallback] = useState(false);

  const validateMermaidSyntax = (chart, diagramType) => {
    if (!chart || typeof chart !== 'string' || chart.trim().length === 0) {
      console.log('❌ Validation failed: Empty or invalid chart');
      return false;
    }

    const trimmedChart = chart.trim();
    const lines = trimmedChart.split('\n').map(line => line.trim()).filter(line => line.length > 0);

    const hasBalancedBrackets = (str) => {
      const stack = [];
      const map = { '(': ')', '[': ']', '{': '}' };
      for (let i = 0; i < str.length; i++) {
        if (map[str[i]]) {
          stack.push(map[str[i]]);
        } else if (Object.values(map).includes(str[i])) {
          if (stack.pop() !== str[i]) return false;
        }
      }
      return stack.length === 0;
    };

    if (!hasBalancedBrackets(trimmedChart)) {
      console.log('❌ Syntax validation failed: Unbalanced brackets/parentheses');
      return false;
    }

    if (diagramType === 'mindmap') {
      if (!trimmedChart.startsWith('mindmap')) return false;
      if (!lines.some(line => line.includes('root'))) return false;
      if (lines.length < 3) return false; // mindmap, root, one child
      console.log('✅ Mindmap validation passed');
      return true;
    } else { // flowchart
      const validStarters = ['graph TD', 'graph LR', 'graph TB', 'flowchart TD', 'flowchart LR', 'flowchart TB'];
      const hasValidStarter = validStarters.some(s => trimmedChart.toLowerCase().startsWith(s.toLowerCase()));
      if (!hasValidStarter) {
        console.log('❌ Flowchart validation failed: Invalid starter. Expected one of:', validStarters);
        console.log('❌ Actual chart start:', trimmedChart.substring(0, 50));
        return false;
      }
      
      const connections = (trimmedChart.match(/-->|---|==>/g) || []).length;
      if (connections === 0) {
        console.log('❌ Flowchart validation failed: No connections found');
        console.log('❌ Chart content:', trimmedChart.substring(0, 200));
        return false;
      }

      // More lenient node validation - just check if we have at least one node definition
      const hasNodes = lines.some(line => {
        const trimLine = line.trim();
        return trimLine.includes('[') || trimLine.includes('(') || trimLine.includes('{') || trimLine.includes('-->');
      });
      
      if (!hasNodes) {
        console.log('❌ Flowchart validation failed: No valid nodes found');
        return false;
      }

      console.log('✅ Flowchart validation passed');
      return true;
    }
  };

  useEffect(() => {
    if (containerRef.current) {
      // Debug logging
      console.log('🔍 MermaidDiagram received:', { 
        type, 
        topic, 
        subject, 
        chart: chart ? `Chart available (${chart.length} chars)` : 'NO CHART',
        chartPreview: chart ? chart.substring(0, 100) + '...' : 'null'
      });
      
      // Check if we have valid AI-generated content
      if (chart && typeof chart === 'string' && chart.trim().length > 0) {
        console.log('✅ Rendering AI Mermaid content');
        setIsLoading(true);
        setError(null);
        setShowFallback(false);
        renderAIMermaidContent();
      } else {
        console.log('❌ No chart content, showing message');
        setIsLoading(false);
        setError('No content generated');
        showNoContentMessage();
      }
    }
  }, [type, topic, subject, chart]);

  const renderAIMermaidContent = async () => {
    if (!containerRef.current || !chart) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Clean the chart content and ensure it's valid Mermaid syntax
      let cleanChart = chart.trim();
      
      console.log('🧠 Cleaning chart content:', cleanChart.substring(0, 200));
      
      // Remove markdown code blocks if present
      cleanChart = cleanChart.replace(/```mermaid\n?/g, '').replace(/```\n?/g, '');
      
      // Fix common syntax issues for Mermaid 10.9.4
      cleanChart = cleanChart.replace(/graph TD/gi, 'graph TD');
      cleanChart = cleanChart.replace(/graph LR/gi, 'graph LR');
      
      // Special handling for mindmaps in Mermaid 10.9.4
      if (type === 'mindmap' && cleanChart.startsWith('mindmap')) {
        console.log('🗺️ Processing mindmap syntax for Mermaid 10.9.4');
        
        // Remove unsupported syntax for Mermaid 10.9.4
        cleanChart = cleanChart
          .replace(/::icon\([^)]+\)\n?/g, '') // Remove icon syntax
          .replace(/:::.*$/gm, '')            // Remove class assignments
          .replace(/^\s*click\s+.*$/gm, '')   // Remove click events
          .replace(/^\s*style\s+.*$/gm, '')   // Remove style definitions
          .replace(/^classDef.*$/gm, '');     // Remove class definitions
        
        // Clean up any empty lines
        cleanChart = cleanChart.replace(/\n\s*\n/g, '\n').trim();
        
        // Ensure proper mindmap formatting
        const lines = cleanChart.split('\n');
        const fixedLines = [];
        let foundRoot = false;
        
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];
          const trimmedLine = line.trim();
          
          if (trimmedLine === 'mindmap') {
            fixedLines.push('mindmap');
            continue;
          }
          
          if (trimmedLine.startsWith('root') && !foundRoot) {
            foundRoot = true;
            // Ensure root node is properly formatted for Mermaid 10.9.4
            const rootMatch = trimmedLine.match(/root\s*"(.+?)"\s*$/);
            if (rootMatch) {
              fixedLines.push(`  root("${rootMatch[1]}")`);
            } else {
              const simpleRootMatch = trimmedLine.match(/root\s*\((.+?)\)\s*$/);
              if (simpleRootMatch) {
                fixedLines.push(`  root("${simpleRootMatch[1]}")`);
              } else {
                fixedLines.push('  root("Main Topic")');
              }
            }
          } else if (trimmedLine && !trimmedLine.startsWith('mindmap') && !trimmedLine.startsWith('root')) {
            // Process other nodes - ensure proper indentation and formatting
            const indentLevel = line.search(/\S/);
            const baseIndent = indentLevel >= 0 ? Math.max(2, indentLevel + 2) : 2;
            const indent = ' '.repeat(baseIndent);
            
            // Clean node text
            let nodeText = trimmedLine
              .replace(/^[\-\*\+]\s*/, '') // Remove bullet points
              .replace(/^["']/, '')        // Remove leading quotes
              .replace(/["']$/, '');       // Remove trailing quotes
            
            if (nodeText && nodeText.length > 0) {
              fixedLines.push(`${indent}${nodeText}`);
            }
          }
        }
        
        // If no root was found, add one
        if (!foundRoot) {
          fixedLines.splice(1, 0, '  root("Main Topic")');
        }
        
        cleanChart = fixedLines.join('\n');
        console.log('🗺️ Fixed mindmap syntax:', cleanChart.substring(0, 300));
      }
      
      // Special handling for flowcharts
      if (type === 'flowchart' && (cleanChart.startsWith('graph') || cleanChart.startsWith('flowchart'))) {
        console.log('📊 Processing flowchart syntax for Mermaid 10.9.4');
        
        // Remove unsupported syntax for Mermaid 10.9.4
        cleanChart = cleanChart
          .replace(/^classDef.*$/gm, '')      // Remove class definitions
          .replace(/^\s*style\s+.*$/gm, '')   // Remove style definitions
          .replace(/^\s*click\s+.*$/gm, '')   // Remove click events
          .replace(/^\s*subgraph.*$/gm, '')   // Remove subgraph definitions
          .replace(/^\s*end\s*$/gm, '')       // Remove standalone end statements
          .replace(/\[end\]/gi, '[End]')      // Fix reserved keyword 'end'
          .replace(/\(end\)/gi, '(End)')
          .replace(/\{end\}/gi, '{End}');
        
        // Clean up any empty lines
        cleanChart = cleanChart.replace(/\n\s*\n/g, '\n').trim();
        
        console.log('📊 Fixed flowchart syntax:', cleanChart.substring(0, 300));
      }
      
      // Debug: Log the cleaned chart before validation
      console.log('🔍 Cleaned chart for validation:', cleanChart);
      console.log('🔍 Chart type:', type);
      
      // Validate Mermaid syntax more thoroughly
      if (!validateMermaidSyntax(cleanChart, type)) {
        console.log('❌ Chart validation failed, switching to fallback');
        throw new Error(`Invalid ${type} syntax - diagram structure validation failed`);
      }
      
      console.log('✅ Chart syntax validated, rendering...');
      
      // Load Mermaid if not already loaded
      await loadMermaid();
      
      // Create unique ID for this chart
      const chartId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      // Create container with the chart content
      containerRef.current.innerHTML = `
        <div id="${chartId}" class="mermaid" style="
          width: 100%; 
          height: 100%; 
          display: flex; 
          align-items: center; 
          justify-content: center;
          background: white;
          overflow: auto;
          padding: 20px;
          text-align: center;
        ">${cleanChart}</div>
      `;
      
      // Initialize Mermaid for this specific element with error handling
      const element = document.getElementById(chartId);
      if (element && window.mermaid) {
        try {
          // Configure Mermaid for better compatibility
          window.mermaid.initialize({ 
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            logLevel: 'debug',
            flowchart: {
              useMaxWidth: true,
              htmlLabels: true
            },
            mindmap: {
              useMaxWidth: true
            },
            themeVariables: {
              primaryColor: '#fff',
              primaryTextColor: '#333'
            }
          });
          
          await window.mermaid.run({
            nodes: [element]
          });
          console.log('✅ Mermaid diagram rendered successfully');
          setIsLoading(false);
        } catch (mermaidError) {
          console.error('❌ Mermaid rendering error:', mermaidError.message);
          throw new Error(`Mermaid rendering failed: ${mermaidError.message}`);
        }
      } else {
        throw new Error('Failed to find chart element or Mermaid not loaded');
      }
      
    } catch (error) {
      console.error('❌ Mermaid rendering failed:', error.message);
      setError(error.message);
      setIsLoading(false);
      
      // Show visual fallback instead of error message
      console.log('🎨 Switching to visual fallback diagram');
      setShowFallback(true);
    }
  };
  
  const loadMermaid = () => {
    return new Promise((resolve, reject) => {
      if (window.mermaid) {
        console.log('✅ Mermaid already loaded');
        resolve();
        return;
      }
      
      console.log('💾 Loading Mermaid library...');
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10.9.4/dist/mermaid.min.js';
      script.onload = () => {
        console.log('✅ Mermaid library loaded');
        window.mermaid.initialize({ 
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose',
          logLevel: 'debug',
          flowchart: {
            useMaxWidth: true,
            htmlLabels: true
          },
          themeVariables: {
            primaryColor: '#fff',
            primaryTextColor: '#333'
          }
        });
        resolve();
      };
      script.onerror = () => {
        console.error('❌ Failed to load Mermaid library');
        reject(new Error('Failed to load Mermaid library'));
      };
      document.head.appendChild(script);
    });
  };

  const showNoContentMessage = () => {
    if (!containerRef.current) return;
    
    containerRef.current.innerHTML = `
      <div style="
        font-family: 'Segoe UI', sans-serif;
        background: #f8f9fa;
        padding: 40px;
        text-align: center;
        border: 2px dashed #dee2e6;
        border-radius: 8px;
        color: #6c757d;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      ">
        <div style="font-size: 24px; margin-bottom: 16px;">📋</div>
        <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
          ${type === 'flowchart' ? 'Flowchart' : 'Mind Map'} Generation in Progress
        </div>
        <div style="font-size: 14px; line-height: 1.5;">
          Our AI is working to create relevant educational content for your question.<br>
          Please try asking your question again for the best results.
        </div>
      </div>
    `;
  };
  
  // If we should show fallback, render the visual diagram
  if (showFallback && chart) {
    return (
      <div style={{ 
        width: '100%', 
        minHeight: '400px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#fff',
        padding: '20px'
      }}>
        <VisualDiagram 
          type={type} 
          chart={chart} 
          title={`${topic || subject || 'Educational'} ${type === 'flowchart' ? 'Process Flow' : 'Concept Map'}`}
        />
      </div>
    );
  }

  return (
    <div 
      ref={containerRef} 
      style={{ 
        width: '100%', 
        minHeight: '400px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#fff'
      }}
    />
  );
};

export default MermaidDiagram;
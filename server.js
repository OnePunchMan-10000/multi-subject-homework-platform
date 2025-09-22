const express = require('express');
const cors = require('cors');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5005; // Changed from 5004 to 5005 to avoid conflicts

// Middleware
app.use(cors());
app.use(express.json());

// File upload configuration
const upload = multer({ storage: multer.memoryStorage() });

// AI Service configuration - Use environment variables (no hardcoded secrets)
const HUGGING_FACE_API_KEY = process.env.HUGGING_FACE_API_KEY || '';
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || '';
// Preferred default: more reliable models
const OPENROUTER_MODEL = process.env.OPENROUTER_MODEL || 'openai/gpt-4o-mini';
const HUGGING_FACE_MODEL = process.env.HUGGING_FACE_MODEL || 'deepset/roberta-base-squad2';

// Subjects configuration
const subjects = [
  { id: 1, name: 'Physics', active: true },
  { id: 2, name: 'Chemistry', active: false },
  { id: 3, name: 'Mathematics', active: false },
  { id: 4, name: 'Biology', active: false },
  { id: 5, name: 'Computer Science', active: false },
  { id: 6, name: 'Engineering', active: false }
];

// Enhanced educational question analysis
function analyzeEducationalQuestion(question) {
  const lowerQuestion = question.toLowerCase();
  
  // Physics concept detection
  const physicsConcepts = {
    mechanics: ['force', 'mass', 'acceleration', 'velocity', 'momentum', 'energy', 'work', 'power'],
    waves: ['wave', 'frequency', 'wavelength', 'amplitude', 'interference', 'diffraction', 'reflection', 'refraction'],
    electricity: ['current', 'voltage', 'resistance', 'capacitor', 'inductor', 'circuit', 'ohm', 'power'],
    thermodynamics: ['heat', 'temperature', 'entropy', 'thermodynamics', 'calorimetry'],
    optics: ['light', 'lens', 'mirror', 'refraction', 'reflection', 'prism', 'interference', 'diffraction'],
    modern: ['quantum', 'relativity', 'photon', 'electron', 'atom', 'nucleus', 'radioactivity']
  };
  
  // Detect question type
  let questionType = 'definition';
  if (lowerQuestion.includes('difference') || lowerQuestion.includes('compare') || lowerQuestion.includes('vs')) {
    questionType = 'comparison';
  } else if (lowerQuestion.includes('how') || lowerQuestion.includes('process') || lowerQuestion.includes('steps')) {
    questionType = 'process';
  } else if (lowerQuestion.includes('why') || lowerQuestion.includes('reason') || lowerQuestion.includes('cause')) {
    questionType = 'explanation';
  } else if (lowerQuestion.includes('calculate') || lowerQuestion.includes('formula') || lowerQuestion.includes('equation')) {
    questionType = 'calculation';
  }
  
  // Detect specific physics concepts
  const detectedConcepts = [];
  for (const [category, concepts] of Object.entries(physicsConcepts)) {
    for (const concept of concepts) {
      if (lowerQuestion.includes(concept)) {
        detectedConcepts.push({ category, concept });
      }
    }
  }
  
  return {
    questionType,
    detectedConcepts,
    hasPhysicsTerms: detectedConcepts.length > 0
  };
}

// Enhanced dynamic content generation functions
function generateDynamicDefinition(question, analysis) {
  if (!analysis.hasPhysicsTerms) return null;
  
  const concept = analysis.detectedConcepts[0]?.concept || 'physics concept';
  return `Definition of ${concept} with relevant formulas, units, and examples`;
}

function generateDynamicComparison(question, analysis) {
  if (analysis.questionType !== 'comparison') return null;
  
  // Extract compared concepts
  const match = question.match(/(?:difference|compare|vs)\s+(.+?)\s+(?:and|vs|versus)\s+(.+)/i);
  if (!match) return null;
  
  const concept1 = match[1].trim();
  const concept2 = match[2].trim();
  
  return `Comparison between ${concept1} and ${concept2} with formulas, units, and examples`;
}

function generateDynamicProcess(question, analysis) {
  if (analysis.questionType !== 'process') return null;
  
  const concept = analysis.detectedConcepts[0]?.concept || 'physics process';
  return `Step-by-step process of ${concept} with explanations and formulas`;
}

// Enhanced AI Service Functions with multiple model fallbacks (optimized for reliability)
async function generateAnswer(question, context = '') {
  const prompt = `Provide a comprehensive, detailed explanation for: "${question}"

${context ? `Context: ${context}` : ''}

Structure your answer with these sections using bold headings:

**Definition and Overview**
- Clear, precise definition of the concept
- Key terminology and vocabulary
- Historical context or discovery (if relevant)

**Fundamental Principles**
- Core scientific principles involved
- Underlying mechanisms and processes
- How and why the phenomenon occurs

**Mathematical Relationships**
- Key formulas and equations
- Variable definitions and units
- Step-by-step derivations (when appropriate)
- Numerical examples with calculations

**Physical Mechanisms**
- Detailed explanation of what happens physically
- Energy considerations and transformations
- Cause-and-effect relationships

**Real-World Applications**
- Practical examples and uses
- Technology implementations
- Everyday phenomena that demonstrate the concept

**Problem-Solving Approach**
- How to approach related problems
- Common techniques and methods
- Tips for avoiding common mistakes

**Related Concepts**
- Connections to other scientific principles
- Advanced topics for further study

Make the explanation educational, comprehensive, and suitable for learning. Include specific examples, calculations, and practical applications where relevant.`;

  // Prioritize DeepSeek v3 as primary model for reliability and cost-effectiveness
  const candidateModels = [
    'deepseek/deepseek-chat-v3.1:free', // Best free model
    'deepseek/deepseek-chat-v3-0324:free', // Alternative DeepSeek
    'meta-llama/llama-3.1-8b-instruct:free', // Free alternative
    'openai/gpt-4o-mini' // Paid fallback
  ].filter(Boolean);

  for (const currentModel of candidateModels) {
    try {
      console.log(`[Answer] Trying model: ${currentModel}`);
      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: currentModel,
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 1000, // Increased for comprehensive, detailed answers
          temperature: 0.3 // Balanced for educational content
        },
        {
          headers: {
            'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json',
            'X-Title': 'Educational AI Assistant'
          }
          // Remove timeout constraint to allow longer responses
        }
      );

      if (response.data && response.data.choices && response.data.choices[0]) {
        console.log(`✅ API call successful with model: ${currentModel}`);
        const answer = response.data.choices[0].message.content;
        
        // Accept any non-empty answer
        if (answer && answer.trim().length > 0) {
          return answer;
        } else {
          console.log(`❌ ${currentModel} generated empty or invalid answer`);
          continue;
        }
      }
      throw new Error('Empty response');
    } catch (apiError) {
      console.log(`❌ Model ${currentModel} failed:`, apiError.response?.data?.error || apiError.message);
      continue;
    }
  }

  console.log('❌ All models failed, returning comprehensive fallback response');
  // Enhanced fallback response with detailed, educational content
  const questionLower = question.toLowerCase();

  let fallbackAnswer = `**Definition and Overview**
**${question}** is a fundamental concept in physics that describes how light behaves when it encounters the boundary between two different media. This phenomenon is essential for understanding how light travels, bends, and reflects in various materials and applications.

**Fundamental Principles**
Light is an electromagnetic wave that travels at approximately 3 × 10⁸ m/s in vacuum. When light encounters a boundary between two media with different optical properties, it can either reflect back into the original medium or refract into the second medium. The behavior depends on:
- The angle of incidence (angle between incident ray and normal)
- The refractive indices of both media
- The nature of the boundary

**Mathematical Relationships**
The key mathematical relationships governing this behavior are:

**Law of Reflection:**
θᵢ = θᵣ
Where θᵢ is the angle of incidence and θᵣ is the angle of reflection.

**Snell's Law (Law of Refraction):**
n₁sinθ₁ = n₂sinθ₂
Where n₁ and n₂ are the refractive indices of medium 1 and 2, and θ₁ and θ₂ are the angles from the normal.

**Refractive Index:**
n = c/v
Where c is the speed of light in vacuum and v is the speed in the medium.

**Critical Angle for Total Internal Reflection:**
θc = sin⁻¹(n₂/n₁) where n₁ > n₂

**Physical Mechanisms**
When light travels from one medium to another:
1. The frequency of light remains constant
2. The wavelength changes based on the medium's refractive index
3. The speed changes according to the medium's optical density
4. At the boundary, part of the light reflects and part refracts
5. The direction change follows the principle of least time (Fermat's principle)

**Real-World Applications**
- **Fiber Optics:** Total internal reflection enables high-speed internet and telecommunications
- **Lenses:** Refraction in eyeglasses, cameras, and telescopes focuses light
- **Prisms:** Used in spectrometers to separate light into different wavelengths
- **Mirrors:** Reflection in periscopes, telescopes, and laser systems
- **Medical Imaging:** Endoscopes use optical fibers for internal examination
- **Photography:** Camera lenses use refraction to form images

**Problem-Solving Approach**
1. Identify the type of problem (reflection vs refraction)
2. Determine the refractive indices of the media involved
3. Apply the appropriate law (reflection or Snell's law)
4. Check for total internal reflection conditions
5. Consider real-world applications and constraints

**Related Concepts**
- Wave-particle duality of light
- Interference and diffraction phenomena
- Polarization of light waves
- Optical path length calculations
- Dispersion in different media

This comprehensive understanding of light behavior forms the foundation for optics, photonics, and numerous technological applications in modern society.`;

  if (questionLower.includes('reflection') || questionLower.includes('refraction') || questionLower.includes('light')) {
    // Keep the optical fallback above
  } else {
    // Generic comprehensive fallback
    fallbackAnswer = `**Definition and Overview**
**${question}** represents a fundamental principle in physics/engineering that involves complex interactions between physical quantities. This concept is crucial for understanding how natural phenomena occur and how they can be applied in practical situations.

**Fundamental Principles**
The concept involves several key principles:
- **Conservation Laws:** Energy, momentum, and other quantities are conserved
- **Equilibrium Conditions:** Systems tend toward stable states
- **Force Interactions:** Understanding how forces cause motion and deformation
- **Material Properties:** How different materials respond to various conditions

**Mathematical Relationships**
Key mathematical relationships include:

**Basic Formula Structure:**
Variable₁ = f(Variable₂, Variable₃, ...)
Where specific relationships depend on the particular case.

**Physical Mechanisms**
The underlying mechanisms involve:
1. **Cause and Effect:** Understanding what drives the phenomenon
2. **Energy Transfer:** How energy moves through the system
3. **Material Response:** How materials react to external stimuli
4. **System Dynamics:** How components interact and influence each other

**Real-World Applications**
- **Engineering Design:** Used in structural analysis and system design
- **Technology Development:** Applied in various technological innovations
- **Scientific Research:** Fundamental to understanding natural processes
- **Problem Solving:** Essential for analytical thinking and solution development

**Problem-Solving Approach**
1. **Identify Key Variables:** Determine what quantities are known and unknown
2. **Apply Appropriate Principles:** Choose the correct physical laws or principles
3. **Use Mathematical Tools:** Apply formulas and perform calculations
4. **Consider Boundary Conditions:** Account for system limitations and constraints
5. **Verify Results:** Check calculations and ensure physical reasonableness

**Related Concepts**
- Connected to other fundamental principles in physics and engineering
- Forms the basis for more advanced topics and applications
- Essential for understanding complex systems and phenomena
- Applied across multiple scientific and engineering disciplines

This concept provides a foundation for understanding how the physical world works and how we can harness these principles for practical applications.`;
  }

  return fallbackAnswer;
}


async function generateFlowchart(question) {
  // Optimized fallback models for flowchart generation (prioritize free models)
  const fallbackModels = [
    'deepseek/deepseek-chat-v3.1:free', // Best free model
    'deepseek/deepseek-chat-v3-0324:free', // Alternative DeepSeek
    'meta-llama/llama-3.1-8b-instruct:free', // Free alternative
    'openai/gpt-4o-mini' // Paid fallback
  ];
  
  for (let i = 0; i < fallbackModels.length; i++) {
    const currentModel = fallbackModels[i];
    
    try {
      const prompt = `Create a comprehensive Mermaid flowchart for: "${question}".

Requirements:
- Start with: graph TD
- Create a logical, step-by-step flow that explains the concept thoroughly
- Include key principles, formulas, conditions, and outcomes
- Use descriptive node labels that are educational (up to 30 words per node)
- Show decision points, processes, and results
- Make it visually structured and easy to follow
- Include relevant scientific principles, mathematical relationships, or key steps
- Connect concepts logically to show cause-and-effect relationships

Example structure:
- Start with the main concept/question
- Break down into key components or steps
- Show relationships and dependencies
- Include conditions or decision points
- End with conclusions or applications

Make the flowchart educational and comprehensive, not just a simple diagram.`;

      console.log(`📋 Trying flowchart generation with model: ${currentModel}`);
      
      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: currentModel,
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 500, // Increased for comprehensive flowcharts
          temperature: 0.5 // Adjusted for better balance
        },
        {
          headers: {
            'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json',
            'X-Title': 'Educational AI Assistant'
          }
          // Remove timeout constraint for flowchart generation
        }
      );

      if (!response.data || !response.data.choices || !response.data.choices[0]) {
        console.log(`❌ ${currentModel} returned invalid response for flowchart`);
        continue;
      }

      let aiChart = response.data.choices[0].message.content;
      
      // Clean and validate the AI-generated Mermaid syntax
      aiChart = aiChart.trim();
      
      // Remove any markdown blocks
      aiChart = aiChart.replace(/```mermaid\n?/g, '').replace(/```\n?/g, '');

      // Strip unsupported/unsafe lines and fix reserved keywords
      aiChart = aiChart
        .replace(/^classDef.*$/gmi, '')
        .replace(/^style\s+.*$/gmi, '')
        .replace(/^click\s+.*$/gmi, '')
        .replace(/^subgraph.*$/gmi, '')
        .replace(/^end\s*$/gmi, '')
        // Fix reserved keyword 'end' in node labels
        .replace(/\[end\]/gi, '[End]')
        .replace(/\(end\)/gi, '(End)')
        .replace(/\{end\}/gi, '{End}');

      // Ensure it starts with a valid flowchart declaration
      if (!aiChart.startsWith('graph TD') && !aiChart.startsWith('graph LR') && !aiChart.startsWith('graph TB') && 
          !aiChart.startsWith('flowchart TD') && !aiChart.startsWith('flowchart LR') && !aiChart.startsWith('flowchart TB')) {
        // Try to coerce by prepending a valid starter
        if (aiChart.startsWith('graph') || aiChart.startsWith('flowchart')) {
          // If it starts with graph/flowchart but not a valid direction, fix it
          aiChart = aiChart.replace(/^(graph|flowchart)\s*/i, 'graph TD\n');
        } else {
          // Prepend a valid starter
          aiChart = 'graph TD\n' + aiChart;
        }
      }
      
      // Validate starter now - accept both graph and flowchart syntax
      const validStarters = ['graph TD', 'graph LR', 'graph TB', 'flowchart TD', 'flowchart LR', 'flowchart TB'];
      const hasValidStarter = validStarters.some(starter => 
        aiChart.toLowerCase().startsWith(starter.toLowerCase())
      );
      if (!hasValidStarter) {
        console.log(`❌ ${currentModel} generated invalid flowchart syntax (after coercion)`);
        continue;
      }
      
      // Validate connections
      const hasConnections = aiChart.includes('-->') || aiChart.includes('---') || aiChart.includes('==>');
      if (!hasConnections) {
        console.log(`❌ ${currentModel} generated flowchart missing connections`);
        continue;
      }
      
      // Ensure all nodes use square brackets format for Mermaid 10.9.4 compatibility
      aiChart = aiChart.replace(/\b([A-Z])\(([^)]*)\)/g, '$1[$2]'); // Convert parentheses to square brackets
      
      console.log(`✅ ${currentModel} generated valid flowchart`);
      return aiChart;
      
    } catch (error) {
      console.log(`❌ ${currentModel} flowchart generation failed:`, error.message);
      continue;
    }
  }
  
  console.log('❌ All models failed for flowchart generation, returning manual flowchart');
  
  // Create more comprehensive fallback flowchart based on question type
  const questionLower = question.toLowerCase();
  
  if (questionLower.includes('reflection') || questionLower.includes('refraction') || questionLower.includes('light')) {
    return `graph TD
    A[Question: ${question}] --> B[Understand Light Behavior]
    B --> C[Light travels as electromagnetic waves]
    C --> D[Light encounters boundary between two media]
    D --> E{Type of interaction?}
    E -->|Same medium boundary| F[Reflection occurs]
    E -->|Different media| G[Refraction occurs]
    F --> H[Apply Law of Reflection: θi = θr]
    G --> I[Apply Snell's Law: n₁sinθ₁ = n₂sinθ₂]
    H --> J[Calculate angles and directions]
    I --> J
    J --> K[Consider special cases]
    K --> L[Total Internal Reflection when θc exceeded]
    K --> M[Normal refraction when θ < θc]
    L --> N[Applications: Fiber optics, Prisms]
    M --> O[Applications: Lenses, Windows]
    N --> P[Real-world examples and problem solving]
    O --> P`;
  } else {
    return `graph TD
    A[Question: ${question}] --> B[Break down into key components]
    B --> C[Identify fundamental principles involved]
    C --> D[Determine relevant formulas and equations]
    D --> E{What type of analysis needed?}
    E -->|Conceptual| F[Define key terms and relationships]
    E -->|Mathematical| G[Apply mathematical models]
    E -->|Practical| H[Consider real-world applications]
    F --> I[Explain underlying mechanisms]
    G --> J[Solve equations and calculate results]
    H --> K[Identify practical examples]
    I --> L[Connect to broader scientific principles]
    J --> L
    K --> L
    L --> M[Verify results and check units]
    M --> N[Consider limitations and assumptions]
    N --> O[Draw conclusions and implications]
    O --> P[Apply knowledge to solve problems]`;
  }
}

async function generateFlowSteps(question) {
  // Optimized fallback models for flow steps generation (prioritize free models)
  const fallbackModels = [
    'deepseek/deepseek-chat-v3.1:free', // Best free model
    'deepseek/deepseek-chat-v3-0324:free', // Alternative DeepSeek
    'meta-llama/llama-3.1-8b-instruct:free', // Free alternative
    'openai/gpt-4o-mini' // Paid fallback
  ];
  
  for (let i = 0; i < fallbackModels.length; i++) {
    const currentModel = fallbackModels[i];
    
    try {
      const prompt = `Write brief steps for: "${question}".

Requirements:
- Focus on main question
- Include key formulas if needed
- Keep concise
- Plain text only.`;

      console.log(`📋 Trying flow steps generation with model: ${currentModel}`);
      
      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: currentModel,
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 200, // Ultra-conservative for free tiers
          temperature: 0.7
        },
        {
          headers: {
            'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json',
            'X-Title': 'Educational AI Assistant'
          }
          // Remove timeout constraint
        }
      );

      if (!response.data || !response.data.choices || !response.data.choices[0]) {
        console.log(`❌ ${currentModel} returned invalid response for flow steps`);
        continue;
      }

      const flowSteps = response.data.choices[0].message.content;
      
      // Accept any non-empty response
      if (flowSteps && flowSteps.trim().length > 0) {
        console.log(`✅ ${currentModel} generated valid flow steps`);
        return flowSteps.trim();
      } else {
        console.log(`❌ ${currentModel} generated empty flow steps`);
        continue;
      }
      
    } catch (error) {
      console.log(`❌ ${currentModel} flow steps generation failed:`, error.message);
      continue;
    }
  }
  
  console.log('❌ All models failed for flow steps generation');
  return null;
}

async function generateMindMap(question) {
  // Optimized fallback models for mindmap generation (prioritize free models)
  const fallbackModels = [
    'deepseek/deepseek-chat-v3.1:free', // Best free model
    'deepseek/deepseek-chat-v3-0324:free', // Alternative DeepSeek
    'meta-llama/llama-3.1-8b-instruct:free', // Free alternative
    'openai/gpt-4o-mini' // Paid fallback
  ];
  
  for (let i = 0; i < fallbackModels.length; i++) {
    const currentModel = fallbackModels[i];
    
    try {
      const prompt = `Create a comprehensive Mermaid mindmap for: "${question}".

Requirements:
- Start with: mindmap
- Include root node with the main concept
- Create 4-6 main branches covering different aspects:
  * Fundamental principles/definitions
  * Key formulas and mathematical relationships
  * Physical mechanisms or processes
  * Real-world applications and examples
  * Problem-solving approaches
  * Related concepts and connections
- Each main branch should have 2-4 detailed sub-branches
- Use descriptive, educational labels that teach the concept
- Make it visually organized and comprehensive for learning
- Include specific examples, formulas, and practical applications where relevant

Make the mindmap a complete learning resource that covers all important aspects of the topic.`;

      console.log(`🧠 Trying mindmap generation with model: ${currentModel}`);
      
      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: currentModel,
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 600, // Increased for comprehensive mindmaps
          temperature: 0.5
        },
        {
          headers: {
            'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json',
            'X-Title': 'Educational AI Assistant'
          }
          // Remove timeout constraint for mindmap generation
        }
      );

      if (!response.data || !response.data.choices || !response.data.choices[0]) {
        console.log(`❌ ${currentModel} returned invalid response for mindmap`);
        continue;
      }

      let aiChart = response.data.choices[0].message.content;
      
      // Clean and validate the AI-generated Mermaid mindmap syntax
      aiChart = aiChart.trim();
      
      // Remove any markdown blocks
      aiChart = aiChart.replace(/```mermaid\n?/g, '').replace(/```\n?/g, '');
      
      // Remove unsupported syntax (Mermaid 10.9.4)
      aiChart = aiChart
        .replace(/::icon\([^)]+\)\n?/g, '') // icons
        .replace(/:::.*$/gmi, '')            // class assignments
        .replace(/^\s*click\s+.*$/gmi, '')  // click events
        .replace(/^\s*style\s+.*$/gmi, '')  // styles
        .replace(/^classDef.*$/gmi, '')     // class definitions
        .replace(/\(\(/g, '"')              // fix double parentheses
        .replace(/\)\)/g, '"');
      
      // Collapse blank lines
      aiChart = aiChart.replace(/\n\s*\n/g, '\n');
      
      // Ensure starter exists and keep from first starter
      const mmIdx = aiChart.search(/(?:^|\n)mindmap/i);
      if (mmIdx === -1) {
        aiChart = 'mindmap\n  root("' + (question.length > 30 ? question.substring(0, 30) + '...' : question) + '")\n' + aiChart;
      } else if (mmIdx > 0) {
        aiChart = aiChart.slice(mmIdx).trimStart();
      }
      
      // Ensure root exists and is well-formed with double quotes
      if (!/\n\s*root\s*\("/i.test('\n' + aiChart)) {
        // insert after first line
        const lines = aiChart.split(/\r?\n/);
        if (lines.length > 0 && /^mindmap\s*$/i.test(lines[0])) {
          lines.splice(1, 0, '  root("' + (question.length > 30 ? question.substring(0, 30) + '...' : question) + '")');
          aiChart = lines.join('\n');
        }
      }
      
      // Fix root node to use double quotes
      aiChart = aiChart.replace(/root\s*\(([^)]+)\)/gi, 'root("$1")');
      aiChart = aiChart.replace(/root\s*\[([^\]]+)\]/gi, 'root("$1")');
      
      // Final validation
      if (!aiChart.startsWith('mindmap')) {
        console.log(`❌ ${currentModel} generated invalid mindmap syntax (after coercion)`);
        continue;
      }
      if (!/\n\s*root\s*"/i.test('\n' + aiChart)) {
        console.log(`❌ ${currentModel} generated mindmap missing root node (after coercion)`);
        continue;
      }
      
      // Log the actual mindmap content for debugging
      console.log(`🔍 ${currentModel} mindmap content (first 300 chars):`, aiChart.substring(0, 300));
      
      console.log(`✅ ${currentModel} generated valid mindmap`);
      return aiChart;
      
    } catch (error) {
      console.log(`❌ ${currentModel} mindmap generation failed:`, error.message);
      continue;
    }
  }
  
  console.log('❌ All models failed for mindmap generation, returning manual mindmap');
  
  // Create comprehensive fallback mindmap based on question type
  const questionLower = question.toLowerCase();
  
  if (questionLower.includes('reflection') || questionLower.includes('refraction') || questionLower.includes('light')) {
    return `mindmap
  root("${question}")
    Fundamental Principles
      Light as electromagnetic waves
      Wave-particle duality
      Speed of light c = 3×10⁸ m/s
      Frequency and wavelength relationship
    Mathematical Laws
      Law of Reflection: θᵢ = θᵣ
      Snell's Law: n₁sinθ₁ = n₂sinθ₂
      Refractive index n = c/v
      Critical angle θc = sin⁻¹(n₂/n₁)
    Physical Mechanisms
      Light interaction with matter
      Change in wave speed at boundaries
      Phase changes upon reflection
      Total internal reflection conditions
    Applications
      Fiber optic communications
      Camera and telescope lenses
      Eyeglasses and contact lenses
      Prisms and optical instruments
    Problem Solving
      Identify incident and refracted rays
      Apply appropriate law or formula
      Consider boundary conditions
      Check for total internal reflection
    Related Concepts
      Dispersion and rainbow formation
      Polarization of light
      Interference and diffraction
      Optical path length`;
  } else {
    return `mindmap
  root("${question}")
    Fundamental Concepts
      Core definitions and terminology
      Basic principles and laws
      Historical development
      Scientific significance
    Mathematical Framework
      Key equations and formulas
      Variable relationships
      Units and dimensions
      Calculation methods
    Physical Mechanisms
      Underlying processes
      Cause and effect relationships
      Energy considerations
      System interactions
    Practical Applications
      Real-world examples
      Technology implementations
      Industrial uses
      Everyday phenomena
    Problem-Solving Approach
      Identify given information
      Choose appropriate methods
      Apply relevant formulas
      Verify results and units
    Connected Topics
      Related scientific principles
      Cross-disciplinary connections
      Advanced concepts
      Current research areas`;
  }
}

async function generateQuiz(question) {
  // Optimized fallback models for quiz generation (prioritize free models)
  const fallbackModels = [
    'deepseek/deepseek-chat-v3.1:free', // Best free model
    'deepseek/deepseek-chat-v3-0324:free', // Alternative DeepSeek
    'meta-llama/llama-3.1-8b-instruct:free', // Free alternative
    'openai/gpt-4o-mini' // Paid fallback
  ];
  for (let i = 0; i < fallbackModels.length; i++) {
    const currentModel = fallbackModels[i];

    try {
      const prompt = `Create 3 comprehensive quiz questions about: "${question}".

Requirements:
- Questions should be directly relevant to the main topic
- Include conceptual understanding, application, and analysis questions
- Provide detailed, educational explanations that teach the concept
- Make explanations comprehensive with formulas, examples, and real-world applications where applicable

Return JSON format:
{
  "questions": [
    {
      "question": "Detailed question that tests understanding of the core concept?",
      "options": ["A) Comprehensive option with context", "B) Well-explained alternative", "C) Detailed incorrect option", "D) Another well-reasoned choice"],
      "correct": "A",
      "explanation": "Comprehensive explanation that includes: 1) Why this answer is correct, 2) Key principles involved, 3) Relevant formulas or equations, 4) Real-world applications or examples, 5) Common misconceptions to avoid"
    }
  ]
}

Focus on educational value and ensure each explanation teaches the student something valuable about the topic.`;

      console.log(`🤔 Trying quiz generation with model: ${currentModel}`);
      
      const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: currentModel,
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 800, // Increased for detailed explanations
          temperature: 0.3
        },
        {
          headers: {
            'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json',
            'X-Title': 'Educational AI Assistant'
          }
          // Remove timeout constraint for quiz generation
        }
      );

      if (!response.data || !response.data.choices || !response.data.choices[0]) {
        console.log(`❌ ${currentModel} returned invalid response for quiz`);
        continue;
      }

      let aiQuiz = response.data.choices[0].message.content;
      
      // Clean and parse the AI-generated JSON
      aiQuiz = aiQuiz.trim();
      
      // Remove any markdown blocks
      aiQuiz = aiQuiz.replace(/```json\n?/g, '').replace(/```\n?/g, '');
      
      // Debug: Log what the AI returned
      console.log(`🔍 ${currentModel} quiz raw response (first 200 chars):`, aiQuiz.substring(0, 200));
      
      try {
        // Try to parse as JSON
        const parsedQuiz = JSON.parse(aiQuiz);
        
        // Debug: Log the parsed structure
        console.log(`🔍 ${currentModel} parsed quiz structure:`, Object.keys(parsedQuiz));
        
        // More flexible validation - check for any quiz structure
        if (parsedQuiz.questions && Array.isArray(parsedQuiz.questions) && parsedQuiz.questions.length > 0) {
          console.log(`✅ ${currentModel} generated valid quiz with ${parsedQuiz.questions.length} questions`);
          return parsedQuiz;
        } else if (Array.isArray(parsedQuiz) && parsedQuiz.length > 0) {
          // Handle case where AI returns array directly
          console.log(`✅ ${currentModel} generated valid quiz array`);
          return { questions: parsedQuiz };
        } else {
          console.log(`❌ ${currentModel} generated invalid quiz structure - missing questions array`);
          continue;
        }
      } catch (parseError) {
        console.log(`❌ ${currentModel} generated invalid JSON:`, parseError.message);
        // Try to extract JSON from the response
        const jsonMatch = aiQuiz.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          try {
            const extractedJson = JSON.parse(jsonMatch[0]);
            if (extractedJson.questions && Array.isArray(extractedJson.questions) && extractedJson.questions.length > 0) {
              console.log(`✅ ${currentModel} extracted valid quiz from response`);
              return extractedJson;
            }
          } catch (extractError) {
            console.log(`❌ ${currentModel} failed to extract valid JSON:`, extractError.message);
          }
        }
        continue;
      }
      
    } catch (error) {
      console.log(`❌ ${currentModel} quiz generation failed:`, error.message);
      continue;
    }
  }
  // If we reach here, all models failed
  console.log('❌ All models failed for quiz generation, returning manual quiz');
  
  // Create more relevant fallback quiz based on the question topic
  const questionLower = question.toLowerCase();
  let fallbackQuestions = [];
  
  // Physics-specific fallback questions
  if (questionLower.includes('reflection') || questionLower.includes('refraction') || questionLower.includes('light')) {
    fallbackQuestions = [
      {
        question: `What is the fundamental principle behind ${question}?`,
        options: [
          "A) Light behaves as both wave and particle, following specific laws of physics",
          "B) Light only travels in straight lines without any deviation", 
          "C) Light properties are completely random and unpredictable",
          "D) Light behavior depends only on its color"
        ],
        correct: "A",
        explanation: "Light exhibits wave-particle duality and follows fundamental laws of physics. In reflection and refraction, light follows Snell's law (n₁sinθ₁ = n₂sinθ₂) and the law of reflection (angle of incidence = angle of reflection). These phenomena occur due to the interaction of light waves with different media, changing their speed and direction. Real-world applications include lenses, mirrors, fiber optics, and optical instruments."
      },
      {
        question: "Which mathematical relationship is crucial for understanding optical phenomena?",
        options: [
          "A) E = mc²",
          "B) Snell's Law: n₁sinθ₁ = n₂sinθ₂",
          "C) F = ma",
          "D) PV = nRT"
        ],
        correct: "B",
        explanation: "Snell's Law (n₁sinθ₁ = n₂sinθ₂) is fundamental for understanding refraction, where n is the refractive index and θ is the angle from the normal. This law explains how light bends when passing between different media. The refractive index indicates how much light slows down in a medium compared to vacuum. This principle is essential in designing lenses, prisms, and understanding phenomena like total internal reflection."
      },
      {
        question: "What practical applications demonstrate the importance of understanding optical principles?",
        options: [
          "A) Only academic research with no real-world use",
          "B) Fiber optic communications, camera lenses, eyeglasses, and medical endoscopes",
          "C) Only simple mirrors and basic lighting",
          "D) Limited to telescope design only"
        ],
        correct: "B",
        explanation: "Optical principles have vast practical applications: Fiber optic cables use total internal reflection for high-speed internet communication; camera and eyeglass lenses use refraction to focus light correctly; medical endoscopes use optical fibers to see inside the human body; microscopes and telescopes use combinations of lenses and mirrors to magnify images. Understanding these principles enables technological advances in telecommunications, medicine, photography, and scientific research."
      }
    ];
  } else {
    // General fallback questions
    fallbackQuestions = [
      {
        question: `What is the fundamental concept behind "${question}"?`,
        options: [
          "A) A complex principle requiring deep understanding of underlying mechanisms and relationships",
          "B) A simple rule that can be memorized without understanding", 
          "C) An outdated concept with no modern relevance",
          "D) A purely theoretical idea with no practical applications"
        ],
        correct: "A",
        explanation: "Most scientific and educational concepts involve complex principles that require understanding the underlying mechanisms, relationships between variables, and how they apply in different contexts. True mastery comes from comprehending the 'why' behind phenomena, not just memorizing facts. This deeper understanding enables problem-solving, prediction, and application to new situations. The concept likely involves specific formulas, laws, or principles that govern its behavior and can be applied to solve real-world problems."
      },
      {
        question: "What approach is most effective for mastering this topic?",
        options: [
          "A) Memorizing definitions without understanding context",
          "B) Understanding principles, practicing applications, and connecting to real-world examples",
          "C) Skipping mathematical relationships and formulas",
          "D) Focusing only on theoretical aspects without practical applications"
        ],
        correct: "B",
        explanation: "Effective learning requires a multi-faceted approach: 1) Understanding fundamental principles and their derivations, 2) Learning relevant mathematical relationships and when to apply them, 3) Practicing problem-solving with various scenarios, 4) Connecting concepts to real-world applications and examples, 5) Understanding common misconceptions and how to avoid them. This comprehensive approach builds both conceptual understanding and practical problem-solving skills."
      },
      {
        question: "Why is understanding the mathematical relationships important for this concept?",
        options: [
          "A) Mathematics is unnecessary for understanding natural phenomena",
          "B) Formulas provide quantitative tools for prediction, calculation, and practical application",
          "C) Mathematical relationships are only useful for academic exercises",
          "D) Equations make concepts more complicated than necessary"
        ],
        correct: "B",
        explanation: "Mathematical relationships are crucial because they: 1) Provide precise, quantitative descriptions of phenomena, 2) Enable accurate predictions and calculations, 3) Allow for practical applications and engineering solutions, 4) Reveal underlying patterns and relationships between variables, 5) Facilitate scientific communication and reproducibility. Understanding the mathematics helps bridge the gap between conceptual knowledge and practical problem-solving abilities."
      }
    ];
  }
  
  return { questions: fallbackQuestions };
}

// Routes
app.get('/api/subjects', (req, res) => {
  res.json(subjects);
});

// Individual endpoints for flowchart and mindmap generation
app.post('/generate-flowchart', async (req, res) => {
  try {
    const { question, subject } = req.body;
    const flowchart = await generateFlowchart(question);
    res.json({ flowchart });
  } catch (error) {
    console.error('Error generating flowchart:', error);
    res.status(500).json({ flowchart: null });
  }
});

app.post('/generate-mindmap', async (req, res) => {
  try {
    const { question, subject } = req.body;
    const mindmap = await generateMindMap(question);
    res.json({ mindmap });
  } catch (error) {
    console.error('Error generating mindmap:', error);
    res.status(500).json({ mindmap: null });
  }
});

app.post('/generate-flowsteps', async (req, res) => {
  try {
    const { question, subject } = req.body;
    const flowsteps = await generateFlowSteps(question);
    res.json({ flowsteps });
  } catch (error) {
    console.error('Error generating flow steps:', error);
    res.status(500).json({ flowsteps: null });
  }
});

app.post('/api/ask', async (req, res) => {
  try {
    const { question, subject } = req.body;
    if (!question) {
      return res.status(400).json({ error: 'Question is required' });
    }

    // Remove unused withTimeout function since we're not using timeouts anymore
    // const withTimeout = (p, ms, name) => new Promise((resolve, reject) => {
    //   const timer = setTimeout(() => {
    //     console.log(`[Timeout] ${name} took too long`);
    //     resolve(null);
    //   }, ms);

    //   p.then(result => {
    //     clearTimeout(timer);
    //     resolve(result);
    //   }).catch(error => {
    //     clearTimeout(timer);
    //     console.error(`[Error] ${name} failed:`, error);
    //     resolve(null);
    //   });
    // });

    console.log('🔧 Starting API generation with API key:', OPENROUTER_API_KEY ? 'SET' : 'MISSING');
    
    // Remove timeout constraints to allow full generation
    const [answer, flowchart, flowsteps, mindmap, quiz] = await Promise.all([
      generateAnswer(question),
      generateFlowchart(question),
      generateFlowSteps(question),
      generateMindMap(question),
      generateQuiz(question)
    ]);
    
    console.log('🔧 Generation results:', {
      answer: answer ? `Generated (${answer.length} chars)` : 'Failed',
      flowchart: flowchart ? `Generated (${flowchart.length} chars)` : 'Failed',
      flowsteps: flowsteps ? `Generated (${flowsteps.length} chars)` : 'Failed', 
      mindmap: mindmap ? `Generated (${mindmap.length} chars)` : 'Failed',
      quiz: quiz ? 'Generated' : 'Failed'
    });

    // Ensure we always return a valid response
    const response = {
      question,
      answer: answer || `We're working on generating a detailed answer for your question: "${question}". Please try again in a moment for the complete response.`,
      pedagogical: {
        flowchart: flowchart || null,
        flowsteps: flowsteps || null,
        mindmap: mindmap || null,
        quiz: quiz || null
      }
    };

    res.json(response);
  } catch (error) {
    console.error('Error in /api/ask:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      question: req.body.question,
      answer: `We encountered an issue while processing your question: "${req.body.question}". Please try again later.`,
      pedagogical: {
        flowchart: null,
        flowsteps: null,
        mindmap: null,
        quiz: null
      }
    });
  }
});

app.post('/api/ask-pdf', upload.single('pdf'), async (req, res) => {
  try {
    const { question } = req.body;
    const pdfFile = req.file;

    if (!question || !pdfFile) {
      return res.status(400).json({ error: 'Question and PDF file are required' });
    }

    // Extract text from PDF
    const pdfData = await pdfParse(pdfFile.buffer);
    const pdfText = pdfData.text || '';

    // Find relevant context from PDF with a tight timeout
    const contextPrompt = `From the following text, extract the most relevant information to answer this question: "${question}"

Text: ${pdfText.substring(0, 3000)}

Extract relevant context:`;

    let relevantContext = null;
    try {
      const contextResponse = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
          model: 'openai/gpt-4o-mini',
          messages: [{ role: 'user', content: contextPrompt }],
          max_tokens: 500
        },
        {
          headers: {
            'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );
      relevantContext = contextResponse.data?.choices?.[0]?.message?.content || null;
    } catch (ctxErr) {
      console.log('Context extraction failed:', ctxErr.message);
    }

    // Generate answer quickly using the extracted context (if any)
    const answer = await generateAnswer(question, relevantContext || '');

    res.json({
      question,
      answer,
      context: relevantContext
    });
  } catch (error) {
    console.error('Error in /api/ask-pdf:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log('🚀 Educational Q&A Platform API Ready!');
  console.log('API Keys configured:');
  console.log('- OpenRouter:', OPENROUTER_API_KEY ? 'Set' : 'Not set');
  console.log('- Hugging Face:', HUGGING_FACE_API_KEY ? 'Set' : 'Not set');
  console.log('- Model:', OPENROUTER_MODEL);
});

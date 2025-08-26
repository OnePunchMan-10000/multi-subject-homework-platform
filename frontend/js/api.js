// ===== API COMMUNICATION =====

class API {
  static BASE_URL = 'https://multi-subject-homework-platform-production.up.railway.app';
  
  static async request(endpoint, options = {}) {
    const url = `${this.BASE_URL}${endpoint}`;
    const token = localStorage.getItem('authToken');
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      return {
        success: response.ok,
        data: data,
        status: response.status,
        message: data.message || data.detail || (response.ok ? 'Success' : 'Request failed')
      };
    } catch (error) {
      console.error('API Error:', error);
      return {
        success: false,
        message: 'Network error. Please check your connection.',
        error: error.message
      };
    }
  }

  static async login(username, password) {
    // Use form data for OAuth2PasswordRequestForm compatibility
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${this.BASE_URL}/auth/login`, {
      method: 'POST',
      body: formData
    });
    
    try {
      const data = await response.json();
      
      if (response.ok && data.access_token) {
        // Get user info
        const userResponse = await this.request('/auth/me', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${data.access_token}`
          }
        });
        
        if (userResponse.success) {
          return {
            success: true,
            token: data.access_token,
            user: userResponse.data,
            message: 'Login successful'
          };
        } else {
          return {
            success: false,
            message: 'Login succeeded but failed to get user info'
          };
        }
      } else {
        return {
          success: false,
          message: data.detail || data.message || 'Invalid credentials'
        };
      }
    } catch (error) {
      return {
        success: false,
        message: 'Login failed. Please try again.'
      };
    }
  }

  static async register(username, password) {
    return await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
  }

  static async getSolution(question, subject) {
    // This would typically call your Streamlit backend or LLM service
    // For now, we'll simulate the API call
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock response - replace with actual API call
      const mockSolution = this.generateMockSolution(question, subject);
      
      return {
        success: true,
        solution: mockSolution,
        message: 'Solution generated successfully'
      };
    } catch (error) {
      return {
        success: false,
        message: 'Failed to generate solution'
      };
    }
  }

  static generateMockSolution(question, subject) {
    // This is a mock solution generator
    // Replace with actual API call to your LLM service
    
    const solutions = {
      'Mathematics': `
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 1:</span> Identify the problem type</h4>
          <p>This appears to be a ${question.includes('equation') ? 'linear equation' : 'mathematical'} problem.</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 2:</span> Apply the appropriate method</h4>
          <p>For the given problem "${question}", we need to follow these steps...</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 3:</span> Solve step by step</h4>
          <p>Working through the calculation systematically...</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Final Answer:</span></h4>
          <p style="background: #f0f9ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #0ea5e9;">
            The solution demonstrates the step-by-step approach to solving this type of problem.
          </p>
        </div>
      `,
      
      'Physics': `
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 1:</span> Identify given information</h4>
          <p>From the problem "${question}", we can identify the key variables and constants.</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 2:</span> Choose the relevant physics principles</h4>
          <p>This problem involves fundamental physics concepts that we need to apply.</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 3:</span> Apply formulas and solve</h4>
          <p>Using the appropriate physics equations and solving systematically...</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Final Answer:</span></h4>
          <p style="background: #f0f9ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #0ea5e9;">
            The physics solution shows how to approach this type of problem methodically.
          </p>
        </div>
      `,
      
      'default': `
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 1:</span> Analyze the question</h4>
          <p>Let's break down your question: "${question}"</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 2:</span> Apply ${subject} concepts</h4>
          <p>Using relevant ${subject} principles and methodologies...</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Step 3:</span> Provide detailed explanation</h4>
          <p>Working through the solution systematically...</p>
        </div>
        
        <div class="solution-step">
          <h4><span style="color: #10b981;">Final Answer:</span></h4>
          <p style="background: #f0f9ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #0ea5e9;">
            This demonstrates a structured approach to solving ${subject} problems.
          </p>
        </div>
      `
    };
    
    return solutions[subject] || solutions['default'];
  }

  static async saveHistory(subject, question, answer) {
    return await this.request('/history', {
      method: 'POST',
      body: JSON.stringify({ subject, question, answer })
    });
  }

  static async getHistory(limit = 25) {
    return await this.request(`/history?limit=${limit}`, {
      method: 'GET'
    });
  }

  static async getUserProfile() {
    return await this.request('/auth/me', {
      method: 'GET'
    });
  }
}

// Export for use in other files
window.API = API;

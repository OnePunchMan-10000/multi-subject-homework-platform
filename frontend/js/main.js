// ===== MAIN APPLICATION LOGIC =====

class EduLLMApp {
  constructor() {
    this.currentPage = 'landing';
    this.user = null;
    this.selectedSubject = null;
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.checkAuthStatus();
    this.hideLoading();
    this.showPage('landing');
  }

  hideLoading() {
    setTimeout(() => {
      const loading = document.getElementById('loading');
      if (loading) {
        loading.style.opacity = '0';
        setTimeout(() => loading.remove(), 300);
      }
    }, 1000);
  }

  setupEventListeners() {
    // Handle navigation
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-page]')) {
        e.preventDefault();
        const page = e.target.getAttribute('data-page');
        this.showPage(page);
      }

      if (e.target.matches('[data-subject]')) {
        e.preventDefault();
        const subject = e.target.getAttribute('data-subject');
        this.selectSubject(subject);
      }

      if (e.target.matches('[data-action]')) {
        e.preventDefault();
        const action = e.target.getAttribute('data-action');
        this.handleAction(action, e.target);
      }
    });

    // Handle form submissions
    document.addEventListener('submit', (e) => {
      if (e.target.matches('#loginForm')) {
        e.preventDefault();
        this.handleLogin(e.target);
      }

      if (e.target.matches('#questionForm')) {
        e.preventDefault();
        this.handleQuestion(e.target);
      }
    });

    // Handle login tab switching
    document.addEventListener('click', (e) => {
      if (e.target.matches('.login-tab')) {
        const targetTab = e.target.getAttribute('data-tab');
        
        // Remove active class from all tabs and contents
        document.querySelectorAll('.login-tab').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.login-tab-content').forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding content
        e.target.classList.add('active');
        document.querySelector(`[data-tab="${targetTab}"].login-tab-content`).classList.add('active');
      }
    });
  }

  checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      this.user = JSON.parse(user);
      if (this.currentPage === 'landing' || this.currentPage === 'login') {
        this.showPage('subjects');
      }
    }
  }

  showPage(pageName) {
    this.currentPage = pageName;
    const app = document.getElementById('app');
    
    // Add page transition class
    app.classList.add('page-transitioning');
    
    setTimeout(() => {
      switch(pageName) {
        case 'landing':
          app.innerHTML = this.renderLandingPage();
          break;
        case 'login':
          app.innerHTML = this.renderLoginPage();
          break;
        case 'subjects':
          app.innerHTML = this.renderSubjectsPage();
          break;
        case 'questions':
          app.innerHTML = this.renderQuestionsPage();
          break;
        case 'profile':
          app.innerHTML = this.renderProfilePage();
          break;
        default:
          app.innerHTML = this.renderLandingPage();
      }
      
      app.classList.remove('page-transitioning');
      app.classList.add('page-entering');
      
      setTimeout(() => app.classList.remove('page-entering'), 500);
    }, 150);
  }

  renderLandingPage() {
    return `
      <div class="page landing-page">
        <!-- Landing Page - Matching your design exactly -->
        <div class="landing-hero">
          <div class="container">
            <!-- Crown Logo -->
            <div class="brand-logo">
              <div class="crown-icon">👑</div>
              <div class="brand-letter">E</div>
            </div>
            
            <!-- Main Title -->
            <h1 class="landing-title">EduLLM</h1>
            
            <!-- Subtitle -->
            <p class="landing-subtitle">
              Your AI-powered homework companion. Get instant, accurate answers
              to your school questions using cutting-edge Large Language Model
              technology.
            </p>
            
            <!-- CTA Buttons -->
            <div class="cta-buttons">
              <button class="btn btn-primary-gold" data-page="login">Start Learning</button>
              <button class="btn btn-outline-gold">Learn More</button>
            </div>
          </div>
          
          <!-- Decorative Background Elements -->
          <div class="hero-decoration">
            <div class="decoration-blob blob-1"></div>
            <div class="decoration-blob blob-2"></div>
          </div>
        </div>

        <!-- Why Choose EduLLM Section -->
        <div class="features-section">
          <div class="container">
            <h2 class="section-title">Why Choose <span class="text-gold">EduLLM?</span></h2>
            
            <div class="features-grid-landing">
              <div class="feature-card-landing">
                <div class="feature-icon-landing">🧠</div>
                <h3>AI-Powered Learning</h3>
                <p>Advanced LLM technology helps you understand complex concepts with personalized explanations.</p>
              </div>
              
              <div class="feature-card-landing">
                <div class="feature-icon-landing">📖</div>
                <h3>Multiple Subjects</h3>
                <p>Get help with Math, Science, History, English, and more - all in one platform.</p>
              </div>
              
              <div class="feature-card-landing">
                <div class="feature-icon-landing">💡</div>
                <h3>Instant Solutions</h3>
                <p>Get step-by-step solutions to your homework problems in seconds.</p>
              </div>
              
              <div class="feature-card-landing">
                <div class="feature-icon-landing">👥</div>
                <h3>Student Community</h3>
                <p>Join thousands of students who are already improving their grades with EduLLM.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Ready to Ace Section -->
        <div class="cta-section">
          <div class="container">
            <h2 class="cta-title">Ready to Ace Your Homework?</h2>
            <p class="cta-subtitle">
              Join thousands of students who are already using EduLLM to improve their
              understanding and grades.
            </p>
            <button class="btn btn-primary-gold btn-lg" data-page="login">Get Started Today</button>
          </div>
        </div>
      </div>
    `;
  }

  renderLoginPage() {
    return `
      <div class="page login-page">
        <!-- Navigation Bar -->
        <nav class="navbar-login">
          <div class="container">
            <div class="nav-brand-login">
              <div class="crown-icon-small">👑</div>
              <span class="brand-text">EduLLM</span>
            </div>
            <div class="nav-links-login">
              <a href="#" data-page="landing">Home</a>
              <a href="#" class="active">Subjects</a>
              <a href="#" data-page="profile">Profile</a>
              <a href="#" data-page="about">About Us</a>
              <button class="btn btn-outline-small" data-page="login">Login</button>
            </div>
          </div>
        </nav>

        <div class="login-main">
          <div class="container">
            <!-- Logo Section -->
            <div class="login-brand">
              <div class="brand-logo-login">
                <div class="crown-icon">👑</div>
                <div class="brand-letter">E</div>
              </div>
              <h1 class="login-brand-title">Welcome to EduLLM</h1>
              <p class="login-brand-subtitle">Sign in to start learning</p>
            </div>

            <!-- Login Form Container -->
            <div class="login-form-container">
              <!-- Tab Navigation -->
              <div class="login-tabs">
                <button class="login-tab active" data-tab="login">Login</button>
                <button class="login-tab" data-tab="signup">Sign Up</button>
              </div>

              <!-- Login Form -->
              <div class="login-tab-content active" data-tab="login">
                <h2 class="form-title">Sign In</h2>
                <p class="form-subtitle">Enter your credentials to access your account</p>

                <form id="loginForm">
                  <div class="form-group">
                    <label class="form-label">Email</label>
                    <div class="input-with-icon">
                      <i class="fas fa-envelope"></i>
                      <input 
                        type="email" 
                        name="username" 
                        class="form-input" 
                        placeholder="student@example.com"
                        required
                      >
                    </div>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Password</label>
                    <div class="input-with-icon">
                      <i class="fas fa-lock"></i>
                      <input 
                        type="password" 
                        name="password" 
                        class="form-input" 
                        placeholder="••••••••"
                        required
                      >
                      <button type="button" class="password-toggle">
                        <i class="fas fa-eye"></i>
                      </button>
                    </div>
                  </div>

                  <button type="submit" class="btn btn-primary-gold btn-full">
                    Sign In
                  </button>
                </form>

                <!-- Social Login -->
                <div class="social-login">
                  <p class="social-divider">OR CONTINUE WITH</p>
                  <div class="social-buttons">
                    <button class="btn btn-social">
                      <i class="fab fa-google"></i>
                      Google
                    </button>
                    <button class="btn btn-social">
                      <i class="fab fa-github"></i>
                      Github
                    </button>
                  </div>
                </div>
              </div>

              <!-- Sign Up Form -->
              <div class="login-tab-content" data-tab="signup">
                <h2 class="form-title">Sign Up</h2>
                <p class="form-subtitle">Create your account to get started</p>

                <form id="signupForm">
                  <div class="form-group">
                    <label class="form-label">Email</label>
                    <div class="input-with-icon">
                      <i class="fas fa-envelope"></i>
                      <input 
                        type="email" 
                        name="email" 
                        class="form-input" 
                        placeholder="student@example.com"
                        required
                      >
                    </div>
                  </div>

                  <div class="form-group">
                    <label class="form-label">Password</label>
                    <div class="input-with-icon">
                      <i class="fas fa-lock"></i>
                      <input 
                        type="password" 
                        name="password" 
                        class="form-input" 
                        placeholder="••••••••"
                        required
                      >
                    </div>
                  </div>

                  <button type="submit" class="btn btn-primary-gold btn-full">
                    Create Account
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderSubjectsPage() {
    const subjects = [
      { id: 'mathematics', name: 'Mathematics', icon: '📐', description: 'Algebra, Calculus, Geometry, Statistics', color: '#4F46E5' },
      { id: 'chemistry', name: 'Chemistry', icon: '🧪', description: 'Organic, Inorganic, Physical Chemistry', color: '#10B981' },
      { id: 'history', name: 'History', icon: '🏛️', description: 'World History, Ancient Civilizations', color: '#F59E0B' },
      { id: 'english', name: 'English', icon: '📚', description: 'Literature, Grammar, Writing', color: '#8B5CF6' },
      { id: 'biology', name: 'Biology', icon: '🧬', description: 'Cell Biology, Genetics, Ecology', color: '#06B6D4' },
      { id: 'economics', name: 'Economics', icon: '💰', description: 'Micro, Macro, International Economics', color: '#F97316' }
    ];

    return `
      <div class="page subjects-page dark-theme">
        <!-- Dark Navigation -->
        <nav class="navbar-dark">
          <div class="container">
            <div class="nav-brand-dark">
              <div class="crown-icon-small">👑</div>
              <span class="brand-text-dark">EduLLM</span>
            </div>
            <div class="nav-links-dark">
              <a href="#" class="nav-link-dark" data-page="landing">Home</a>
              <a href="#" class="nav-link-dark active">Subjects</a>
              <a href="#" class="nav-link-dark" data-page="profile">Profile</a>
              <a href="#" class="nav-link-dark">About Us</a>
              <button class="btn btn-outline-light" data-action="logout">
                <i class="fas fa-user"></i>
                Login
              </button>
            </div>
            <!-- Dark Mode Toggle -->
            <button class="dark-mode-toggle">
              <i class="fas fa-moon"></i>
            </button>
          </div>
        </nav>

        <div class="subjects-main">
          <div class="container">
            <!-- Header -->
            <div class="subjects-header">
              <h1 class="subjects-title">
                Choose Your <span class="text-gold">Subject</span>
              </h1>
              <p class="subjects-subtitle">
                Select a subject to get started with your homework questions. Our AI tutor
                is ready to help!
              </p>
            </div>

            <!-- Subjects Grid -->
            <div class="subjects-grid-dark">
              ${subjects.map(subject => `
                <div class="subject-card-dark" data-subject="${subject.id}" style="--subject-color: ${subject.color}">
                  <div class="subject-card-inner">
                    <div class="subject-icon-dark">${subject.icon}</div>
                    <h3 class="subject-name-dark">${subject.name}</h3>
                    <p class="subject-desc-dark">${subject.description}</p>
                  </div>
                  <div class="subject-card-gradient"></div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderQuestionsPage() {
    return `
      <div class="page questions-page-dark dark-theme">
        <!-- Dark Navigation -->
        <nav class="navbar-dark">
          <div class="container">
            <div class="nav-brand-dark">
              <div class="crown-icon-small">👑</div>
              <span class="brand-text-dark">EduLLM</span>
            </div>
            <div class="nav-links-dark">
              <a href="#" class="nav-link-dark" data-page="landing">Home</a>
              <a href="#" class="nav-link-dark" data-page="subjects">Subjects</a>
              <a href="#" class="nav-link-dark" data-page="profile">Profile</a>
              <a href="#" class="nav-link-dark">About Us</a>
              <button class="btn btn-outline-light" data-action="logout">
                <i class="fas fa-user"></i>
                Login
              </button>
            </div>
            <!-- Dark Mode Toggle -->
            <button class="dark-mode-toggle">
              <i class="fas fa-moon"></i>
            </button>
          </div>
        </nav>

        <div class="container">
          <!-- Questions Header -->
          <div class="questions-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                  <div style="background: var(--primary-gold); padding: 0.5rem; border-radius: 8px;">
                    <i class="fas fa-book" style="color: var(--dark-bg);"></i>
                  </div>
                  <span style="color: var(--primary-gold); font-weight: 600;">${this.selectedSubject}</span>
                </div>
                <h1 class="questions-title">Ask Your <span style="color: var(--primary-gold);">Question</span></h1>
                <p class="questions-subtitle">Get instant, detailed answers to your ${this.selectedSubject} questions</p>
              </div>
              <button class="btn btn-outline-light" data-page="subjects">
                <i class="fas fa-arrow-left"></i>
                Back to Subjects
              </button>
            </div>
          </div>

          <!-- Question Input Section -->
          <div class="question-input-section">
            <h3 class="question-form-title">
              <i class="fas fa-lightbulb"></i>
              What would you like to learn?
            </h3>
            
            <form id="questionForm">
              <textarea 
                id="question" 
                name="question" 
                class="question-textarea" 
                placeholder="Ask any ${this.selectedSubject} question here..."
                required
              ></textarea>
              
              <button type="submit" class="btn-ask-question">
                <i class="fas fa-paper-plane"></i>
                Ask Question
              </button>
            </form>
          </div>

          <!-- Recent Questions -->
          <div class="recent-questions">
            <h3 class="recent-questions-title">
              <i class="fas fa-history"></i>
              Recent Questions
            </h3>
            
            <div class="question-item">
              <div class="question-meta">
                <span class="question-subject">Mathematics</span>
                <span class="question-time">2 hours ago</span>
              </div>
              <div class="question-text">What is the derivative of x^2 + 3x + 2?</div>
              <div class="question-answer">The derivative is 2x + 3</div>
            </div>
            
            <div class="question-item">
              <div class="question-meta">
                <span class="question-subject">${this.selectedSubject}</span>
                <span class="question-time">1 day ago</span>
              </div>
              <div class="question-text">Previous question example for ${this.selectedSubject}</div>
              <div class="question-answer">Detailed explanation would appear here...</div>
            </div>
          </div>

          <div id="solution-container" class="hidden">
            <!-- Solution will be displayed here -->
          </div>
        </div>
      </div>
    `;
  }

  renderProfilePage() {
    return `
      <div class="page profile-page-dark dark-theme">
        <!-- Dark Navigation -->
        <nav class="navbar-dark">
          <div class="container">
            <div class="nav-brand-dark">
              <div class="crown-icon-small">👑</div>
              <span class="brand-text-dark">EduLLM</span>
            </div>
            <div class="nav-links-dark">
              <a href="#" class="nav-link-dark" data-page="landing">Home</a>
              <a href="#" class="nav-link-dark" data-page="subjects">Subjects</a>
              <a href="#" class="nav-link-dark active">Profile</a>
              <a href="#" class="nav-link-dark">About Us</a>
              <button class="btn btn-outline-light" data-action="logout">
                <i class="fas fa-user"></i>
                Login
              </button>
            </div>
            <!-- Dark Mode Toggle -->
            <button class="dark-mode-toggle">
              <i class="fas fa-moon"></i>
            </button>
          </div>
        </nav>

        <div class="container">
          <!-- Profile Header -->
          <div class="profile-header">
            <h1 class="profile-title">My <span style="color: var(--primary-gold);">Profile</span></h1>
            
            <!-- Profile Tabs -->
            <div class="profile-tabs">
              <button class="profile-tab active" data-profile-tab="overview">Overview</button>
              <button class="profile-tab" data-profile-tab="progress">Progress</button>
              <button class="profile-tab" data-profile-tab="settings">Settings</button>
            </div>
          </div>

          <!-- Profile Content -->
          <div class="profile-content">
            <!-- User Info Card -->
            <div class="profile-card">
              <div class="profile-user-info">
                <div class="profile-avatar">JD</div>
                <div class="profile-user-details">
                  <h3>John Doe</h3>
                  <p>john.doe@example.com</p>
                  <p style="color: var(--dark-text-muted); font-size: 0.9rem;">Grade 10</p>
                </div>
              </div>
            </div>

            <!-- Stats Cards -->
            <div class="profile-stats">
              <div class="stat-card">
                <div class="stat-icon">📚</div>
                <div class="stat-number">127</div>
                <div class="stat-label">Questions Asked</div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-number">6</div>
                <div class="stat-label">Subjects Studied</div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">🏆</div>
                <div class="stat-number">15</div>
                <div class="stat-label">Day Streak</div>
              </div>
            </div>

            <!-- Achievements -->
            <div class="profile-card">
              <h3 style="color: var(--dark-text-primary); margin-bottom: 1rem;">Achievements</h3>
              <p style="color: var(--dark-text-secondary); margin-bottom: 2rem;">Your learning milestones</p>
              
              <div class="achievements-grid">
                <div class="achievement-card">
                  <div class="achievement-icon">🏆</div>
                  <div class="achievement-title">First Question</div>
                  <div class="achievement-desc">Asked your first question</div>
                </div>
                
                <div class="achievement-card">
                  <div class="achievement-icon">⚡</div>
                  <div class="achievement-title">Quick Learner</div>
                  <div class="achievement-desc">Completed 10 questions in one day</div>
                </div>
                
                <div class="achievement-card">
                  <div class="achievement-icon">📚</div>
                  <div class="achievement-title">Subject Master</div>
                  <div class="achievement-desc">Reached 90% progress in a subject</div>
                </div>
                
                <div class="achievement-card achievement-locked">
                  <div class="achievement-icon">🔥</div>
                  <div class="achievement-title">Streak Champion</div>
                  <div class="achievement-desc">Maintained a 30-day streak</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  selectSubject(subject) {
    this.selectedSubject = subject.charAt(0).toUpperCase() + subject.slice(1);
    this.showPage('questions');
  }

  async handleLogin(form) {
    const formData = new FormData(form);
    const username = formData.get('username');
    const password = formData.get('password');

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<div class="loading"></div> Signing in...';
    submitBtn.disabled = true;

    try {
      const response = await API.login(username, password);
      
      if (response.success) {
        this.user = response.user;
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        this.showAlert('success', `Welcome back, ${username}!`);
        setTimeout(() => this.showPage('subjects'), 1000);
      } else {
        this.showAlert('error', response.message || 'Login failed');
      }
    } catch (error) {
      this.showAlert('error', 'Connection failed. Please try again.');
    } finally {
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;
    }
  }

  async handleQuestion(form) {
    const formData = new FormData(form);
    const question = formData.get('question');

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<div class="loading"></div> Getting solution...';
    submitBtn.disabled = true;

    try {
      const response = await API.getSolution(question, this.selectedSubject);
      
      if (response.success) {
        this.displaySolution(response.solution);
      } else {
        this.showAlert('error', response.message || 'Failed to get solution');
      }
    } catch (error) {
      this.showAlert('error', 'Failed to get solution. Please try again.');
    } finally {
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;
    }
  }

  displaySolution(solution) {
    const container = document.getElementById('solution-container');
    container.innerHTML = `
      <div class="card fade-in" style="margin-top: var(--spacing-8);">
        <div class="card-header">
          <h2>📚 ${this.selectedSubject} Solution</h2>
        </div>
        <div class="card-body">
          <div class="solution-content">
            ${solution}
          </div>
        </div>
        <div class="card-footer">
          <div style="display: flex; gap: var(--spacing-4); justify-content: center;">
            <button class="btn btn-outline btn-sm" data-action="rate-helpful">
              <i class="fas fa-thumbs-up"></i> Helpful
            </button>
            <button class="btn btn-outline btn-sm" data-action="rate-needs-work">
              <i class="fas fa-thumbs-down"></i> Needs work
            </button>
            <button class="btn btn-outline btn-sm" data-action="try-again">
              <i class="fas fa-redo"></i> Try again
            </button>
          </div>
        </div>
      </div>
    `;
    container.classList.remove('hidden');
    container.scrollIntoView({ behavior: 'smooth' });
  }

  handleAction(action, element) {
    switch(action) {
      case 'logout':
        this.logout();
        break;
      case 'rate-helpful':
        this.showAlert('success', 'Thanks for your feedback!');
        break;
      case 'rate-needs-work':
        this.showAlert('info', "We'll work on improving!");
        break;
      case 'try-again':
        document.getElementById('solution-container').classList.add('hidden');
        document.getElementById('question').focus();
        break;
    }
  }

  logout() {
    this.user = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    this.showPage('landing');
  }

  showAlert(type, message) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} fade-in`;
    alert.innerHTML = message;
    alert.style.position = 'fixed';
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '1000';
    alert.style.minWidth = '300px';
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    }, 3000);
  }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.app = new EduLLMApp();
});

// ===== REUSABLE COMPONENTS =====

class Components {
  static createButton(text, type = 'primary', icon = null, onClick = null) {
    const button = document.createElement('button');
    button.className = `btn btn-${type}`;
    
    if (icon) {
      button.innerHTML = `<i class="${icon}"></i> ${text}`;
    } else {
      button.textContent = text;
    }
    
    if (onClick) {
      button.addEventListener('click', onClick);
    }
    
    return button;
  }

  static createCard(title, content, footer = null) {
    const card = document.createElement('div');
    card.className = 'card';
    
    let cardHTML = '';
    
    if (title) {
      cardHTML += `
        <div class="card-header">
          <h3>${title}</h3>
        </div>
      `;
    }
    
    cardHTML += `
      <div class="card-body">
        ${content}
      </div>
    `;
    
    if (footer) {
      cardHTML += `
        <div class="card-footer">
          ${footer}
        </div>
      `;
    }
    
    card.innerHTML = cardHTML;
    return card;
  }

  static createAlert(type, message, dismissible = true) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    
    let alertHTML = message;
    
    if (dismissible) {
      alertHTML += `
        <button class="alert-dismiss" onclick="this.parentElement.remove()">
          <i class="fas fa-times"></i>
        </button>
      `;
    }
    
    alert.innerHTML = alertHTML;
    return alert;
  }

  static createFormGroup(label, input) {
    const group = document.createElement('div');
    group.className = 'form-group';
    
    group.innerHTML = `
      <label class="form-label">${label}</label>
      ${input.outerHTML}
    `;
    
    return group;
  }

  static createInput(type, name, placeholder = '', required = false) {
    const input = document.createElement('input');
    input.type = type;
    input.name = name;
    input.className = 'form-input';
    input.placeholder = placeholder;
    input.required = required;
    
    return input;
  }

  static createTextarea(name, placeholder = '', rows = 4, required = false) {
    const textarea = document.createElement('textarea');
    textarea.name = name;
    textarea.className = 'form-input form-textarea';
    textarea.placeholder = placeholder;
    textarea.rows = rows;
    textarea.required = required;
    
    return textarea;
  }

  static createModal(title, content, actions = []) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    
    modal.innerHTML = `
      <div class="modal-backdrop" onclick="this.parentElement.remove()"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>${title}</h3>
          <button class="modal-close" onclick="this.closest('.modal').remove()">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          ${content}
        </div>
        ${actions.length ? `
          <div class="modal-footer">
            ${actions.map(action => action.outerHTML).join('')}
          </div>
        ` : ''}
      </div>
    `;
    
    return modal;
  }

  static createLoadingSpinner(size = 'md') {
    const spinner = document.createElement('div');
    spinner.className = `loading loading-${size}`;
    return spinner;
  }

  static createSubjectCard(subject) {
    const card = document.createElement('div');
    card.className = 'subject-card card';
    card.setAttribute('data-subject', subject.id);
    
    card.innerHTML = `
      <div class="subject-icon">${subject.icon}</div>
      <h3 class="subject-title">${subject.name}</h3>
      <p class="subject-description">${subject.description}</p>
      <button class="btn btn-primary" data-subject="${subject.id}">
        Select ${subject.name}
      </button>
    `;
    
    return card;
  }

  static createNavigation(user = null) {
    const nav = document.createElement('nav');
    nav.className = 'navbar';
    
    nav.innerHTML = `
      <div class="nav-container container">
        <div class="nav-brand">
          <i class="fas fa-graduation-cap"></i>
          EduLLM
        </div>
        ${user ? `
          <ul class="nav-menu">
            <li><a href="#" class="nav-link" data-page="subjects">Home</a></li>
            <li><a href="#" class="nav-link" data-page="profile">Profile</a></li>
            <li><a href="#" class="nav-link" data-page="about">About</a></li>
            <li><a href="#" class="nav-link" data-action="logout">Logout</a></li>
          </ul>
        ` : ''}
      </div>
    `;
    
    return nav;
  }

  static createFeatureItem(icon, title, description) {
    const item = document.createElement('div');
    item.className = 'feature-item slide-in-up';
    
    item.innerHTML = `
      <div class="feature-icon">${icon}</div>
      <h3 class="feature-title">${title}</h3>
      <p class="feature-description">${description}</p>
    `;
    
    return item;
  }

  static createSolutionStep(stepNumber, title, content) {
    const step = document.createElement('div');
    step.className = 'solution-step';
    
    step.innerHTML = `
      <h4>
        <span style="color: var(--accent-color);">Step ${stepNumber}:</span> 
        ${title}
      </h4>
      <p>${content}</p>
    `;
    
    return step;
  }

  static createProgressBar(percentage, label = '') {
    const container = document.createElement('div');
    container.className = 'progress-container';
    
    container.innerHTML = `
      ${label ? `<div class="progress-label">${label}</div>` : ''}
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${percentage}%"></div>
      </div>
      <div class="progress-text">${percentage}%</div>
    `;
    
    return container;
  }

  static createToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} fade-in`;
    toast.textContent = message;
    
    // Position toast
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '1000';
    toast.style.minWidth = '300px';
    
    // Add to DOM
    document.body.appendChild(toast);
    
    // Auto remove
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, duration);
    
    return toast;
  }

  static createDropdown(options, placeholder = 'Select option...') {
    const dropdown = document.createElement('div');
    dropdown.className = 'dropdown';
    
    dropdown.innerHTML = `
      <button class="dropdown-toggle" type="button">
        ${placeholder}
        <i class="fas fa-chevron-down"></i>
      </button>
      <div class="dropdown-menu">
        ${options.map(option => `
          <a href="#" class="dropdown-item" data-value="${option.value}">
            ${option.label}
          </a>
        `).join('')}
      </div>
    `;
    
    // Add dropdown functionality
    const toggle = dropdown.querySelector('.dropdown-toggle');
    const menu = dropdown.querySelector('.dropdown-menu');
    
    toggle.addEventListener('click', () => {
      dropdown.classList.toggle('active');
    });
    
    dropdown.addEventListener('click', (e) => {
      if (e.target.matches('.dropdown-item')) {
        e.preventDefault();
        const value = e.target.getAttribute('data-value');
        const label = e.target.textContent;
        
        toggle.innerHTML = `${label} <i class="fas fa-chevron-down"></i>`;
        dropdown.classList.remove('active');
        
        // Dispatch custom event
        dropdown.dispatchEvent(new CustomEvent('change', {
          detail: { value, label }
        }));
      }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('active');
      }
    });
    
    return dropdown;
  }

  static createTabs(tabs) {
    const container = document.createElement('div');
    container.className = 'tabs-container';
    
    const tabsNav = document.createElement('div');
    tabsNav.className = 'tabs-nav';
    
    const tabsContent = document.createElement('div');
    tabsContent.className = 'tabs-content';
    
    tabs.forEach((tab, index) => {
      // Create tab button
      const tabButton = document.createElement('button');
      tabButton.className = `tab-button ${index === 0 ? 'active' : ''}`;
      tabButton.textContent = tab.label;
      tabButton.setAttribute('data-tab', tab.id);
      
      // Create tab content
      const tabPane = document.createElement('div');
      tabPane.className = `tab-pane ${index === 0 ? 'active' : ''}`;
      tabPane.setAttribute('data-tab', tab.id);
      tabPane.innerHTML = tab.content;
      
      tabsNav.appendChild(tabButton);
      tabsContent.appendChild(tabPane);
    });
    
    // Add tab switching functionality
    tabsNav.addEventListener('click', (e) => {
      if (e.target.matches('.tab-button')) {
        const tabId = e.target.getAttribute('data-tab');
        
        // Remove active class from all tabs and panes
        container.querySelectorAll('.tab-button, .tab-pane').forEach(el => {
          el.classList.remove('active');
        });
        
        // Add active class to clicked tab and corresponding pane
        e.target.classList.add('active');
        container.querySelector(`[data-tab="${tabId}"].tab-pane`).classList.add('active');
      }
    });
    
    container.appendChild(tabsNav);
    container.appendChild(tabsContent);
    
    return container;
  }
}

// Export for global use
window.Components = Components;

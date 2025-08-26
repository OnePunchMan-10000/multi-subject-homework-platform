# EduLLM Frontend

This is the professional frontend for the EduLLM application, built with modern HTML, CSS, and JavaScript.

## 📁 Structure

```
frontend/
├── index.html          # Main HTML file
├── css/
│   ├── main.css        # Core styles and variables
│   ├── components.css  # Component-specific styles
│   └── responsive.css  # Mobile responsive styles
├── js/
│   ├── main.js         # Main application logic
│   ├── api.js          # API communication
│   └── components.js   # Reusable UI components
└── README.md          # This file
```

## 🚀 Features

- **Modern Design**: Clean, professional UI with smooth animations
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **Component-Based**: Reusable UI components for easy maintenance
- **API Integration**: Seamless communication with your backend
- **Fast Loading**: Optimized CSS and JavaScript
- **Accessible**: Following web accessibility best practices

## 🎨 Customization

### Colors
Edit the CSS variables in `css/main.css`:

```css
:root {
  --primary-color: #6366f1;    /* Main brand color */
  --secondary-color: #f59e0b;  /* Accent color */
  --text-primary: #1f2937;     /* Main text color */
  --background: #ffffff;       /* Background color */
  /* ... more variables */
}
```

### Components
Add new components in `js/components.js`:

```javascript
static createNewComponent(options) {
  // Your component logic here
}
```

### Pages
Modify page layouts in `js/main.js`:

```javascript
renderCustomPage() {
  return `
    <div class="page custom-page">
      <!-- Your page content -->
    </div>
  `;
}
```

## 📱 Pages

1. **Landing Page**: Welcome screen with features and call-to-action
2. **Login Page**: Clean authentication form
3. **Subjects Page**: Grid of available subjects
4. **Questions Page**: Question input and solution display

## 🔧 Development

### Local Development
1. Open `index.html` in a web browser
2. Or use a local server:
   ```bash
   python -m http.server 8000
   # Then visit http://localhost:8000
   ```

### Integration with Streamlit
The frontend communicates with your Streamlit backend via the API endpoints defined in `js/api.js`.

### Backend URL
Update the backend URL in `js/api.js`:
```javascript
static BASE_URL = 'https://your-backend-url.com';
```

## 🎯 Usage

### Basic Setup
1. Update the backend URL in `js/api.js`
2. Customize colors and branding in `css/main.css`
3. Open `index.html` in a browser

### Adding New Features
1. Add styles to appropriate CSS files
2. Create components in `js/components.js`
3. Add page logic to `js/main.js`
4. Update API calls in `js/api.js`

## 📦 Dependencies

- **Font Awesome**: Icons (loaded via CDN)
- **Google Fonts**: Inter font family (loaded via CDN)
- **No JavaScript frameworks**: Pure vanilla JS for maximum performance

## 🌟 Best Practices

- Use CSS variables for consistent theming
- Follow mobile-first responsive design
- Keep components small and reusable
- Use semantic HTML for accessibility
- Optimize images and assets
- Test across different browsers and devices

## 🔄 Updates

To update the design:
1. Modify CSS variables for global changes
2. Update component styles in `components.css`
3. Add new animations in `main.css`
4. Test responsive behavior in `responsive.css`

## 🚀 Deployment

1. Upload all files to your web server
2. Update API endpoints to production URLs
3. Test all functionality
4. Monitor performance and user experience

---

**Built with ❤️ for EduLLM - Making education accessible through AI**

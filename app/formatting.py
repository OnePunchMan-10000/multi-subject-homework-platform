import re
import html

def format_powers(text):
    """Convert ^2, ^3, etc. to proper superscript format"""
    # Replace common powers with superscript
    text = re.sub(r'\^2', '<span class="power">2</span>', text)
    text = re.sub(r'\^3', '<span class="power">3</span>', text)
    text = re.sub(r'\^4', '<span class="power">4</span>', text)
    text = re.sub(r'\^(\d+)', r'<span class="power">\1</span>', text)
    text = re.sub(r'\^(\([^)]+\))', r'<span class="power">\1</span>', text)
    # Replace sqrt(...) with √(...)
    text = re.sub(r'\bsqrt\s*\(', '√(', text)
    return text


def format_fraction(numerator, denominator):
    """Format a fraction with numerator over denominator in inline style"""
    num_clean = format_powers(numerator.strip())
    den_clean = format_powers(denominator.strip())
    
    return f"""<div class="fraction-display">
        <div>{num_clean}</div>
        <div class="fraction-bar"></div>
        <div>{den_clean}</div>
    </div>"""


def format_response(response_text):
    """Improved formatting with consistent vertical fractions and tighter spacing.

    Also formats Computer Science responses:
    - Preserves fenced code blocks in a styled container
    - Keeps non-code steps readable like math section
    """
    if not response_text:
        return ""
    
    # Clean up LaTeX notation to simple text but preserve fraction structure
    response_text = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', response_text)
    response_text = re.sub(r'\\[a-zA-Z]+\{?([^}]*)\}?', r'\1', response_text)
    
    # Handle fenced code blocks (```lang ... ```)
    formatted_content = []
    code_block_open = False
    code_lines = []
    code_lang = None
    
    lines = response_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            # Add minimal spacing between sections
            if not code_block_open:
                formatted_content.append("<br>")
            continue
        
        # Detect start/end of fenced code blocks
        if line.startswith('```'):
            fence = line.strip()
            if not code_block_open:
                # opening
                code_block_open = True
                code_lines = []
                code_lang = fence.strip('`').strip() or 'text'
            else:
                # closing -> render and reset
                escaped = html.escape("\n".join(code_lines))
                formatted_content.append(
                    f'<div class="code-block"><div class="code-header">{code_lang}</div><pre><code>{escaped}</code></pre></div>'
                )
                code_block_open = False
                code_lines = []
                code_lang = None
            continue
        
        if code_block_open:
            code_lines.append(line)
            continue
        
        # Skip stray closing tags that may appear in the model text
        if re.match(r'^\s*</(div|span|p)>\s*$', line):
            continue
        
        # One-line step headers with next-line explanation in monospace box
        if re.match(r'^\*\*Step \d+:', line) or re.match(r'^###\s*Step \d+:', line):
            step_text = re.sub(r'\*\*|###', '', line).strip()
            # Keep step title on one line
            formatted_content.append(f'<div style="color:#4CAF50;font-weight:700;margin:0.6rem 0 0.2rem 0;">{step_text}</div>')
            # The explanation for this step is expected on the next line; we wrap whatever comes next
            # by inserting an opener token that the next non-empty, non-step line will close.
            formatted_content.append('<!--STEP_CODE_NEXT-->')
        
        # Final answer (simple one-line box, as before)
        elif 'Final Answer' in line:
            clean_line = re.sub(r'\*\*', '', line)
            formatted_content.append(f'<div class="final-answer">{format_powers(clean_line)}</div>\n')
        
        # Check for any line containing fractions - convert ALL to vertical display
        elif '/' in line and ('(' in line or any(char in line for char in ['x', 'y', 'dx', 'dy', 'du', 'dv'])):
            # Convert all fractions in the line to vertical display
            # First handle complex fractions like (numerator)/(denominator) - more comprehensive pattern
            formatted_line = re.sub(r'\(([^)]+)\)\s*/\s*\(([^)]+)\)', lambda m: format_fraction(m.group(1), m.group(2)), line)
            # Then handle simple fractions like du/dx, dv/dx, dy/dx
            formatted_line = re.sub(r'\b([a-zA-Z]+)/([a-zA-Z]+)\b', lambda m: format_fraction(m.group(1), m.group(2)), formatted_line)
            # Handle any remaining fractions with parentheses - catch cases like (2x + 1) / (x² + 1)²
            formatted_line = re.sub(r'\(([^)]+)\)\s*/\s*([^/\s]+)', lambda m: format_fraction(m.group(1), m.group(2)), formatted_line)
            formatted_content.append(f'<div class="math-line">{format_powers(formatted_line)}</div>\n')
        
        
        
        # If we previously saw a step header, wrap this first following line in step-code box
        elif formatted_content and formatted_content[-1] == '<!--STEP_CODE_NEXT-->':
            formatted_content.pop()  # remove token
            formatted_content.append(f'<div class="step-code">{html.escape(line)}</div>')
        
        # Mathematical expressions with equations (no fractions)
        elif ('=' in line and any(char in line for char in ['x', '+', '-', '*', '^', '(', ')'])):
            formatted_content.append(f'<div class="math-line">{format_powers(line)}</div>\n')
        
        # Regular text
        else:
            formatted_content.append(f"{format_powers(line)}\n")
    
    return ''.join(formatted_content)



<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homework Helper</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background-color: #1a1a1a;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .problem-section {
            margin-bottom: 40px;
        }
        
        .section-title {
            color: #ffffff;
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .problem-text {
            color: #cccccc;
            font-size: 16px;
            margin-bottom: 10px;
            line-height: 1.8;
        }
        
        .step-title {
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
            margin: 30px 0 15px 0;
        }
        
        .step-content {
            color: #cccccc;
            font-size: 15px;
            margin-bottom: 15px;
            line-height: 1.7;
        }
        
        .equation {
            background-color: #2a2a2a;
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 15px 20px;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            color: #ffffff;
            margin: 15px 0;
            text-align: left;
        }
        
        .final-answer-section {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #404040;
        }
        
        .final-answer {
            color: #ffffff;
            font-size: 16px;
            font-weight: 500;
        }
        
        .input-section {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #1a1a1a;
            border-top: 1px solid #404040;
            padding: 20px;
        }
        
        .input-container {
            max-width: 900px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .subject-select {
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 10px 15px;
            font-size: 14px;
            min-width: 120px;
        }
        
        .question-input {
            flex: 1;
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 10px 15px;
            font-size: 14px;
            resize: vertical;
            min-height: 40px;
        }
        
        .solve-btn {
            background-color: #4a4a4a;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .solve-btn:hover {
            background-color: #5a5a5a;
        }
        
        .content-area {
            margin-bottom: 100px;
        }
        
        .loading {
            text-align: center;
            color: #888;
            padding: 40px;
        }
        
        ::placeholder {
            color: #888;
        }
        
        :focus {
            outline: none;
            border-color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="content-area" id="content">
            <!-- Example problem displayed by default -->
            <div class="problem-section">
                <div class="section-title">Given</div>
                <div class="problem-text">The quadratic equation to solve is: 2x² + 5x - 3 = 0.</div>
                
                <div class="section-title">To Find</div>
                <div class="problem-text">The values of x that satisfy the equation.</div>
                
                <div class="step-title">Step 1</div>
                <div class="step-content">Identify the coefficients a, b, and c in the quadratic equation ax² + bx + c = 0.</div>
                <div class="equation">a = 2,    b = 5,    c = -3</div>
                
                <div class="step-title">Step 2</div>
                <div class="step-content">Apply the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a.</div>
                
                <div class="step-title">Step 3</div>
                <div class="step-content">Substitute the values of a, b, and c into the quadratic formula and simplify.</div>
                <div class="equation">x = (-5 ± √(5² - 4 • 2 • (-3))) / 2 • 2</div>
                <div class="equation">x = (-5 ± √(25 + 24)) / 4</div>
                <div class="equation">x = (-5 ± √49) / 4</div>
                <div class="equation">x = (-5 ± 7) / 4</div>
                
                <div class="final-answer-section">
                    <div class="section-title">Final Answer</div>
                    <div class="final-answer">The solutions for x are: x = -3/2 or x = 1.</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="input-section">
        <div class="input-container">
            <select class="subject-select" id="subject">
                <option value="Math">Math</option>
                <option value="English">English</option>
                <option value="Science">Science</option>
                <option value="History">History</option>
                <option value="Geography">Geography</option>
                <option value="Physics">Physics</option>
                <option value="Chemistry">Chemistry</option>
                <option value="Biology">Biology</option>
                <option value="Economics">Economics</option>
            </select>
            <textarea class="question-input" id="question" placeholder="Enter your homework question here..." rows="1"></textarea>
            <button class="solve-btn" onclick="solveProblem()">Solve</button>
        </div>
    </div>

    <script>
        // Auto-resize textarea
        const textarea = document.getElementById('question');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });

        // Sample problems for different subjects
        const sampleProblems = {
            "Math": {
                problem: "Solve the quadratic equation: 2x² + 5x - 3 = 0",
                solution: `<div class="problem-section">
                    <div class="section-title">Given</div>
                    <div class="problem-text">The quadratic equation to solve is: 2x² + 5x - 3 = 0.</div>
                    
                    <div class="section-title">To Find</div>
                    <div class="problem-text">The values of x that satisfy the equation.</div>
                    
                    <div class="step-title">Step 1</div>
                    <div class="step-content">Identify the coefficients a, b, and c in the quadratic equation ax² + bx + c = 0.</div>
                    <div class="equation">a = 2,    b = 5,    c = -3</div>
                    
                    <div class="step-title">Step 2</div>
                    <div class="step-content">Apply the quadratic formula: x = (-b ± √(b² - 4ac)) / 2a.</div>
                    
                    <div class="step-title">Step 3</div>
                    <div class="step-content">Substitute the values of a, b, and c into the quadratic formula and simplify.</div>
                    <div class="equation">x = (-5 ± √(5² - 4 • 2 • (-3))) / 2 • 2</div>
                    <div class="equation">x = (-5 ± √(25 + 24)) / 4</div>
                    <div class="equation">x = (-5 ± √49) / 4</div>
                    <div class="equation">x = (-5 ± 7) / 4</div>
                    
                    <div class="final-answer-section">
                        <div class="section-title">Final Answer</div>
                        <div class="final-answer">The solutions for x are: x = -3/2 or x = 1.</div>
                    </div>
                </div>`
            },
            "Physics": {
                problem: "Calculate the force when mass = 10 kg and acceleration = 5 m/s²",
                solution: `<div class="problem-section">
                    <div class="section-title">Given</div>
                    <div class="problem-text">Mass (m) = 10 kg<br>Acceleration (a) = 5 m/s²</div>
                    
                    <div class="section-title">To Find</div>
                    <div class="problem-text">Force (F) acting on the object.</div>
                    
                    <div class="step-title">Step 1</div>
                    <div class="step-content">Apply Newton's second law of motion.</div>
                    <div class="equation">F = ma</div>
                    
                    <div class="step-title">Step 2</div>
                    <div class="step-content">Substitute the given values into the formula.</div>
                    <div class="equation">F = 10 kg × 5 m/s²</div>
                    <div class="equation">F = 50 N</div>
                    
                    <div class="final-answer-section">
                        <div class="section-title">Final Answer</div>
                        <div class="final-answer">The force acting on the object is 50 Newtons (N).</div>
                    </div>
                </div>`
            },
            "Chemistry": {
                problem: "Balance the chemical equation: H₂ + O₂ → H₂O",
                solution: `<div class="problem-section">
                    <div class="section-title">Given</div>
                    <div class="problem-text">Unbalanced equation: H₂ + O₂ → H₂O</div>
                    
                    <div class="section-title">To Find</div>
                    <div class="problem-text">The balanced chemical equation with proper coefficients.</div>
                    
                    <div class="step-title">Step 1</div>
                    <div class="step-content">Count the atoms on both sides of the equation.</div>
                    <div class="equation">Left side: 2 H atoms, 2 O atoms<br>Right side: 2 H atoms, 1 O atom</div>
                    
                    <div class="step-title">Step 2</div>
                    <div class="step-content">Balance oxygen atoms by adding coefficient 2 to H₂O.</div>
                    <div class="equation">H₂ + O₂ → 2H₂O</div>
                    
                    <div class="step-title">Step 3</div>
                    <div class="step-content">Balance hydrogen atoms by adding coefficient 2 to H₂.</div>
                    <div class="equation">2H₂ + O₂ → 2H₂O</div>
                    
                    <div class="final-answer-section">
                        <div class="section-title">Final Answer</div>
                        <div class="final-answer">The balanced equation is: 2H₂ + O₂ → 2H₂O</div>
                    </div>
                </div>`
            }
        };

        function solveProblem() {
            const question = document.getElementById('question').value.trim();
            const subject = document.getElementById('subject').value;
            const content = document.getElementById('content');
            
            if (!question) {
                alert('Please enter a question first!');
                return;
            }
            
            // Show loading state
            content.innerHTML = '<div class="loading">Solving your ' + subject + ' problem...</div>';
            
            // Simulate API call delay
            setTimeout(() => {
                // For demo purposes, show sample problems based on subject
                const sample = sampleProblems[subject];
                if (sample) {
                    content.innerHTML = sample.solution;
                } else {
                    // Generic solution format
                    content.innerHTML = `<div class="problem-section">
                        <div class="section-title">Question</div>
                        <div class="problem-text">${question}</div>
                        
                        <div class="step-title">Analysis</div>
                        <div class="step-content">This is a ${subject} problem that requires step-by-step analysis.</div>
                        
                        <div class="step-title">Step 1</div>
                        <div class="step-content">Identify the key components and concepts involved in this ${subject} problem.</div>
                        
                        <div class="step-title">Step 2</div>
                        <div class="step-content">Apply relevant ${subject} principles and formulas to solve the problem.</div>
                        
                        <div class="step-title">Step 3</div>
                        <div class="step-content">Calculate and verify the solution using appropriate methods.</div>
                        
                        <div class="final-answer-section">
                            <div class="section-title">Solution</div>
                            <div class="final-answer">The solution to this ${subject} problem requires specialized knowledge and calculation.</div>
                        </div>
                    </div>`;
                }
                
                // Clear the input
                document.getElementById('question').value = '';
                document.getElementById('question').style.height = 'auto';
            }, 1500);
        }

        // Allow Enter key to solve (Ctrl+Enter for newline)
        document.getElementById('question').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.ctrlKey) {
                e.preventDefault();
                solveProblem();
            }
        });
    </script>
</body>
</html>

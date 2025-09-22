import React, { useState } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';

const Quiz = ({ quiz }) => {
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);

  if (!quiz || !quiz.questions) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        <p>🧠 Quiz will be generated based on the topic...</p>
      </div>
    );
  }

  const handleAnswerSelect = (questionIndex, optionIndex) => {
    if (showResults) return;
    
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: optionIndex
    }));
  };

  const handleSubmitQuiz = () => {
    if (Object.keys(selectedAnswers).length === quiz.questions.length) {
      setShowResults(true);
    }
  };

  const resetQuiz = () => {
    setSelectedAnswers({});
    setShowResults(false);
  };

  const calculateScore = () => {
    let correct = 0;
    quiz.questions.forEach((question, index) => {
      const selectedOption = selectedAnswers[index];
      const correctAnswer = question.correct;
      
      // Handle both index-based (0,1,2,3) and letter-based (A,B,C,D) answers
      let isCorrect = false;
      if (typeof correctAnswer === 'string' && correctAnswer.match(/^[A-D]$/)) {
        // If correct answer is "A", "B", "C", "D"
        const correctIndex = correctAnswer.charCodeAt(0) - 65; // A=0, B=1, C=2, D=3
        isCorrect = selectedOption === correctIndex;
      } else if (typeof correctAnswer === 'number') {
        // If correct answer is already a number index
        isCorrect = selectedOption === correctAnswer;
      } else {
        // Try to match the option text directly
        const selectedOptionText = question.options[selectedOption];
        isCorrect = selectedOptionText === correctAnswer;
      }
      
      if (isCorrect) {
        correct++;
      }
    });
    return correct;
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return '#28a745';
    if (percentage >= 60) return '#ffc107';
    return '#dc3545';
  };

  const getScoreMessage = (percentage) => {
    if (percentage >= 80) return '🎉 Excellent! You have a strong understanding!';
    if (percentage >= 60) return '👍 Good job! Review the explanations to improve.';
    return '📚 Keep studying! Review the material and try again.';
  };

  const score = showResults ? calculateScore() : 0;
  const percentage = showResults ? Math.round((score / quiz.questions.length) * 100) : 0;

  return (
    <div className="quiz-container">
      {showResults && (
        <div style={{ 
          padding: '20px', 
          marginBottom: '25px', 
          background: `linear-gradient(135deg, ${getScoreColor(percentage)}15, ${getScoreColor(percentage)}25)`,
          border: `2px solid ${getScoreColor(percentage)}`,
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <h3 style={{ color: getScoreColor(percentage), marginBottom: '10px' }}>
            🏆 Quiz Results
          </h3>
          <div style={{ fontSize: '1.2rem', fontWeight: 'bold', marginBottom: '8px' }}>
            Score: {score}/{quiz.questions.length} ({percentage}%)
          </div>
          <p style={{ color: '#666', marginBottom: '15px' }}>
            {getScoreMessage(percentage)}
          </p>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            gap: '15px',
            flexWrap: 'wrap'
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', color: '#28a745' }}>✓</div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Correct: {score}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', color: '#dc3545' }}>✗</div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Wrong: {quiz.questions.length - score}</div>
            </div>
          </div>
        </div>
      )}

      {quiz.questions.map((question, questionIndex) => (
        <div key={questionIndex} className="question">
          <h5 style={{ marginBottom: '15px', color: '#333' }}>
            Question {questionIndex + 1}: {question.question}
          </h5>
          
          <ul className="options">
            {question.options.map((option, optionIndex) => {
              const isSelected = selectedAnswers[questionIndex] === optionIndex;
              
              // Fix correct answer detection
              let isCorrect = false;
              const correctAnswer = question.correct;
              if (typeof correctAnswer === 'string' && correctAnswer.match(/^[A-D]$/)) {
                // If correct answer is "A", "B", "C", "D"
                const correctIndex = correctAnswer.charCodeAt(0) - 65; // A=0, B=1, C=2, D=3
                isCorrect = optionIndex === correctIndex;
              } else if (typeof correctAnswer === 'number') {
                // If correct answer is already a number index
                isCorrect = optionIndex === correctAnswer;
              }
              
              const isIncorrect = showResults && isSelected && !isCorrect;
              
              let className = '';
              if (showResults) {
                if (isCorrect) className = 'correct';
                else if (isIncorrect) className = 'incorrect';
              }

              return (
                <li
                  key={optionIndex}
                  className={`${isSelected ? 'selected' : ''} ${className}`}
                  onClick={() => handleAnswerSelect(questionIndex, optionIndex)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 15px',
                    margin: '8px 0',
                    background: isSelected ? (showResults ? (isCorrect ? '#d4edda' : '#f8d7da') : '#e3f2fd') : 'white',
                    border: `2px solid ${
                      showResults 
                        ? (isCorrect ? '#28a745' : (isIncorrect ? '#dc3545' : '#e1e5e9'))
                        : (isSelected ? '#667eea' : '#e1e5e9')
                    }`,
                    borderRadius: '8px',
                    cursor: showResults ? 'default' : 'pointer',
                    transition: 'all 0.3s ease',
                    transform: isSelected && !showResults ? 'translateX(5px)' : 'none'
                  }}
                >
                  <span style={{ fontWeight: isSelected ? '600' : 'normal' }}>
                    {option.startsWith(String.fromCharCode(65 + optionIndex) + ')') || 
                     option.startsWith(String.fromCharCode(65 + optionIndex) + '.') ? 
                     option : 
                     `${String.fromCharCode(65 + optionIndex)}. ${option}`}
                  </span>
                  <div>
                    {showResults && isCorrect && <CheckCircle size={18} color="#28a745" />}
                    {showResults && isIncorrect && <XCircle size={18} color="#dc3545" />}
                    {isSelected && !showResults && (
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: '#667eea'
                      }} />
                    )}
                  </div>
                </li>
              );
            })}
          </ul>

          {showResults && question.explanation && (
            <div style={{
              marginTop: '15px',
              padding: '15px',
              background: 'linear-gradient(135deg, #f8f9fa, #e9ecef)',
              borderLeft: '4px solid #667eea',
              borderRadius: '8px',
              fontSize: '0.95rem'
            }}>
              <div style={{ 
                fontWeight: 'bold', 
                color: '#667eea', 
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                💡 Explanation:
              </div>
              <div style={{ color: '#444', lineHeight: '1.5' }}>
                {question.explanation}
              </div>
            </div>
          )}
        </div>
      ))}

      <div style={{ textAlign: 'center', marginTop: '25px' }}>
        {!showResults ? (
          <button
            onClick={handleSubmitQuiz}
            disabled={Object.keys(selectedAnswers).length !== quiz.questions.length}
            style={{
              padding: '12px 30px',
              background: Object.keys(selectedAnswers).length === quiz.questions.length 
                ? 'linear-gradient(135deg, #667eea, #764ba2)' 
                : '#e1e5e9',
              color: Object.keys(selectedAnswers).length === quiz.questions.length ? 'white' : '#999',
              border: 'none',
              borderRadius: '8px',
              cursor: Object.keys(selectedAnswers).length === quiz.questions.length ? 'pointer' : 'not-allowed',
              fontSize: '1rem',
              fontWeight: '600',
              transition: 'all 0.3s ease',
              transform: Object.keys(selectedAnswers).length === quiz.questions.length ? 'none' : 'scale(0.95)',
              boxShadow: Object.keys(selectedAnswers).length === quiz.questions.length 
                ? '0 4px 15px rgba(102, 126, 234, 0.3)' 
                : 'none'
            }}
          >
            📈 Submit Quiz ({Object.keys(selectedAnswers).length}/{quiz.questions.length})
          </button>
        ) : (
          <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={resetQuiz}
              style={{
                padding: '12px 25px',
                background: 'linear-gradient(135deg, #6c757d, #495057)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '600',
                transition: 'transform 0.2s ease',
                boxShadow: '0 4px 15px rgba(108, 117, 125, 0.3)'
              }}
              onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
              onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
            >
              🔄 Retake Quiz
            </button>
            <div style={{
              padding: '12px 25px',
              background: `linear-gradient(135deg, ${getScoreColor(percentage)}20, ${getScoreColor(percentage)}30)`,
              color: getScoreColor(percentage),
              border: `2px solid ${getScoreColor(percentage)}`,
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              {percentage >= 80 ? '🏆' : percentage >= 60 ? '👍' : '📚'} 
              Final Score: {percentage}%
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Quiz;
import React from "react";
import "../styles/Questiondisplay.css"; // Import the external CSS

const QuestionDisplay = ({ question, currentQuestion, totalQuestions, selectedOption, onOptionChange }) => {
  return (
    <div className="question-display">
      <h2>{`Question ${currentQuestion + 1} of ${totalQuestions}`}</h2>
      <p className="question-text">{question.question_text}</p>
      <div className="options">
        {question.options.map((option, index) => (
          <div key={index} className="option">
            <label>
              <input
                type="radio"
                value={index}
                checked={selectedOption === index}
                onChange={() => onOptionChange(index)} // Pass index instead of option
              />
              {option}
            </label>
          </div>
        ))}
      </div>
      <button className="unclear-button" onClick={() => onOptionChange(null)}>Unclear</button> {/* Use null for unclear */}
    </div>
  );
};

export default QuestionDisplay;

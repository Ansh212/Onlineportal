import React from "react";
import Timer from "./timer";
import "../styles/Sidepanel.css";

const SidePanel = ({ questions, currentQuestion, onQuestionChange, time, submithandle, isSubmitting, showVideo, toggleVideoPreview }) => {
  return (
    <div className="side-panel">
      <Timer time={time} submithandle={submithandle} />

      <h3 className="side-panel-title">Questions</h3>
      
      {/* List of questions */}
      <ul className="question-list">
        {questions.map((question, index) => (
          <li key={index}>
            <button
              className={index === currentQuestion ? "question-button active" : "question-button"}
              onClick={() => onQuestionChange(index)}
            >
              {`Question ${index + 1}`}
            </button>
          </li>
        ))}
      </ul>

      {/* Toggle button for showing/hiding the WebGazer video */}
      <button className="toggle-video-button" onClick={toggleVideoPreview}>
        {showVideo ? "Hide Video" : "Show Video"}
      </button>
      
      <div className="navigation-buttons">
        {/* Navigate to next question */}
        {currentQuestion < questions.length - 1 && (
          <button className="nav-button" onClick={() => onQuestionChange(currentQuestion + 1)}>Next</button>
        )}

        {/* Navigate to previous question */}
        {currentQuestion > 0 && (
          <button className="nav-button" onClick={() => onQuestionChange(currentQuestion - 1)}>Prev</button>
        )}
      </div>

      {/* Submit button */}
      <button 
        className="submit-button" 
        onClick={() => submithandle()} 
        disabled={isSubmitting} // Disable when submitting
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </div>
  );
};

export default SidePanel;

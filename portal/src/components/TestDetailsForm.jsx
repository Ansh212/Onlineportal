import React from "react";
import '../styles/form.css';

const TestDetailsForm = ({ onSubmit, onCancel }) => {
    const handleStartTest = () => {
        onSubmit(); // Trigger the test start
    };

    return (
        <div className="test-details-container">
            <h2 className="test-details-heading">Ready to Start Your Test</h2>
            <p className="test-details-message">You are going to start a test. Please be prepared.</p>
            
            <div className="test-details-actions">
                <button onClick={handleStartTest} className="start-test-button">Start Test</button>
                <button onClick={onCancel} className="cancel-test-button">Cancel</button>
            </div>
        </div>
    );
};

export default TestDetailsForm;

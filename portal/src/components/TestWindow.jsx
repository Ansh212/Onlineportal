import React, { useState, useEffect, useCallback } from "react";
import SidePanel from "./SidePanel";
import QuestionDisplay from "./QuestionDisplay";
import { useNavigate, useParams } from 'react-router-dom';
import DisableBackButton from "./DisableBackButton";
import "../styles/Testwindow.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000"; 

const TestWindow = () => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(true); 
  const { testId } = useParams();
  const [time, setTime] = useState(0); 
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false); // <-- New state for submission control
  const navigate = useNavigate();
  const userId = localStorage.getItem('userid'); 

  const logactivity = useCallback((activityText, questionId = null) => {
    const logs = JSON.parse(localStorage.getItem(`test_${testId}_logs`)) || [];
    const timestamp = new Date().toISOString();
    const entry = { 
      location: questionId,
      timestamp, 
      activity_text: activityText 
    };
    logs.push(entry);
    localStorage.setItem(`test_${testId}_logs`, JSON.stringify(logs)); 
  }, [testId]);

  useEffect(() => {
    const handleSwitch = () => {
      if (document.visibilityState === "hidden") {
        logactivity(`Tab Switched`, null);
      } else if (document.visibilityState === "visible") {
        logactivity(`Returned to Test Tab`, null);
      }
    };
  
    window.addEventListener('visibilitychange', handleSwitch);
    return () => {
      window.removeEventListener('visibilitychange', handleSwitch);
    };
  }, [logactivity]);
  

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await fetch(`${API_URL}/api/take_test`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            userId: userId,
            testId: testId,
          }),
        });
        const data = await response.json(); 
        
        setQuestions(data.questions); 
        setLoading(false); 

        let storedDeadline = localStorage.getItem(`test_${testId}_deadline`);
        if (!storedDeadline) {
          const newDeadline = Date.now() + data.duration * 60 * 1000; 
          localStorage.setItem(`test_${testId}_deadline`, newDeadline);
          setTime(data.duration*60*1000);  
        } else {
          const remainingTime = storedDeadline - Date.now();
          if (remainingTime <= 0) {
            localStorage.removeItem(`test_${testId}_deadline`);
            navigate("/Dashboard"); 
          } else {
            setTime(remainingTime); 
          }
        }

        const storedOptions = localStorage.getItem(`test_${testId}_selectedOptions`);
        if (!storedOptions) {
          setSelectedOptions(Array(data.questions.length).fill(null));
        } else {
          setSelectedOptions(JSON.parse(storedOptions));
        }

        const started = localStorage.getItem(`test_${testId}_teststarted`);
        if (!started) {
          const currtime = Date.now();
          localStorage.setItem(`test_${testId}_teststarted`, currtime);
          logactivity(`Test Started`, data.questions[0]?._id);
        }

      } catch (error) {
        console.error("Error fetching questions:", error);
      }
    };

    if (testId) {
      fetchQuestions();
    }
  }, [testId, navigate, logactivity, userId]);

  const handleQuestionChange = (index) => {
    setCurrentQuestion(index);
    logactivity(`Selected question ${index}`, questions[index]?._id);
  };

  const submithandle = async () => {
    if (isSubmitting) return; // prevent multiple submissions
    setIsSubmitting(true); // start submission process

    logactivity(`Submitted Test`, questions[questions.length - 1]?._id);
    try {
      const logs = JSON.parse(localStorage.getItem(`test_${testId}_logs`)) || [];
      const userid = localStorage.getItem('userid');
      const centerid = localStorage.getItem('center_id');
  
      const data = {
        userId: userid,
        testId: testId,
        centerId : centerid,
        logs: logs,
      };
  
      const response = await fetch(`${API_URL}/api/submitTest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
  
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error('Failed to send logs to the backend');
      }

      // Clear localStorage for this test
      localStorage.removeItem(`test_${testId}_deadline`);
      localStorage.removeItem(`test_${testId}_selectedOptions`);
      localStorage.removeItem(`test_${testId}_logs`);
      localStorage.removeItem(`test_${testId}_teststarted`);

      // Clear local component state
      setQuestions([]);
      setSelectedOptions([]);
      setTime(0);
      setCurrentQuestion(0);

      // Update test status
      await handleCompleteTest(testId, responseData.score);

      // Navigate back to dashboard
      navigate('/Dashboard');
    } catch (error) {
      console.error("Error during submission:", error);
      setIsSubmitting(false); // reset submission state on error
    }
  };
  

  const handleCompleteTest = (testId, score) => {
    const storedRegisteredTests = JSON.parse(localStorage.getItem('registered_tests')) || [];
    const storedGivenTests = JSON.parse(localStorage.getItem('given_tests')) || [];

    // Find the completed test in registered tests
    const completedTest = storedRegisteredTests.find(test => test._id === testId);

    if (completedTest) {
      // Remove the completed test from registered tests
      const updatedRegisteredTests = storedRegisteredTests.filter(test => test._id !== testId);
      const newGivenTest = { 
        _id: completedTest._id, 
        test_name: completedTest.test_name,
        score: score,
        city: completedTest.city,
        state: completedTest.state,
      };

      localStorage.setItem('registered_tests', JSON.stringify(updatedRegisteredTests));
      localStorage.setItem('given_tests', JSON.stringify([...storedGivenTests, newGivenTest]));
    }
  };


  const handleOptionChange = (questionIndex, option) => {
    const updatedOptions = [...selectedOptions];
    if (option === "unclear") {
      updatedOptions[questionIndex] = null;
      logactivity(`Cleared option for question ${questionIndex}`, questions[questionIndex]?._id);
    } else {
      updatedOptions[questionIndex] = option;
      logactivity(`Selected option ${option} for question ${questionIndex}`, questions[questionIndex]?._id);
    }
    setSelectedOptions(updatedOptions);
    localStorage.setItem(`test_${testId}_selectedOptions`, JSON.stringify(updatedOptions));
  };

  if (loading) {
    return <div>Loading questions...</div>;
  }

  return (
    <div className="test-window" id="test-window">
      <DisableBackButton />
      <SidePanel
        questions={questions}
        currentQuestion={currentQuestion}
        onQuestionChange={handleQuestionChange}
        time={time}
        submithandle={submithandle}
        isSubmitting={isSubmitting} // pass down to disable button
      />
    
      <QuestionDisplay
        question={questions[currentQuestion]}
        currentQuestion={currentQuestion}
        totalQuestions={questions.length}
        selectedOption={selectedOptions[currentQuestion]}
        onOptionChange={(option) => handleOptionChange(currentQuestion, option)}
      />
    </div>
  );
};

export default TestWindow;

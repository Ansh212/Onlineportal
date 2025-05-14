import React, { useState, useEffect, useCallback, useRef } from "react";
import SidePanel from "./SidePanel";
import QuestionDisplay from "./QuestionDisplay";
import { useNavigate, useParams } from 'react-router-dom';
import DisableBackButton from "./DisableBackButton";
import "../styles/Testwindow.css";
import webgazer from 'webgazer';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

const TestWindow = () => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [loading, setLoading] = useState(true);
  const { testId } = useParams();
  const [time, setTime] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const userId = localStorage.getItem('userid');

  const [focusedTime, setFocusedTime] = useState(0);
  const [distractionTime, setDistractionTime] = useState(0);
  const [isGazeInside, setIsGazeInside] = useState(false);
  const [showVideo, setShowVideo] = useState(true);

  const testWindowRef = useRef(null);
  const gazeIntervalRef = useRef(null);
  const webgazerInitialized = useRef(false);
  const isGazeInsideRef = useRef(false);

  const logactivity = useCallback((activityText, questionId = null) => {
    const logs = JSON.parse(localStorage.getItem(`test_${testId}_logs`)) || [];
    const timestamp = new Date().toISOString();
    logs.push({ location: questionId, timestamp, activity_text: activityText });
    localStorage.setItem(`test_${testId}_logs`, JSON.stringify(logs));
  }, [testId]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      logactivity(document.visibilityState === "hidden" ? "Tab Switched" : "Returned to Test Tab");
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [logactivity]);

  useEffect(() => {
    if (!testId) return;

    const fetchQuestions = async () => {
      try {
        const res = await fetch(`${API_URL}/api/take_test`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ userId, testId }),
        });
        const data = await res.json();

        setQuestions(data.questions);
        setLoading(false);

        let storedDeadline = localStorage.getItem(`test_${testId}_deadline`);
        if (!storedDeadline) {
          const deadline = Date.now() + data.duration * 60000;
          localStorage.setItem(`test_${testId}_deadline`, deadline);
          setTime(data.duration * 60000);
        } else {
          const remaining = storedDeadline - Date.now();
          if (remaining <= 0) {
            localStorage.removeItem(`test_${testId}_deadline`);
            navigate("/Dashboard");
          } else {
            setTime(remaining);
          }
        }

        const storedOptions = localStorage.getItem(`test_${testId}_selectedOptions`);
        setSelectedOptions(storedOptions ? JSON.parse(storedOptions) : Array(data.questions.length).fill(null));

        if (!localStorage.getItem(`test_${testId}_teststarted`)) {
          localStorage.setItem(`test_${testId}_teststarted`, Date.now());
          logactivity(`Test Started`, data.questions[0]?._id);
        }
      } catch (err) {
        console.error("Error fetching questions:", err);
      }
    };

    fetchQuestions();
  }, [testId, navigate, logactivity, userId]);

  const handleQuestionChange = useCallback((index) => {
    setCurrentQuestion(index);
    logactivity(`Selected question ${index}`, questions[index]?._id);
  }, [logactivity, questions]);

  const stopWebGazer = useCallback(() => {
    if (!webgazerInitialized.current) return;
  
    clearInterval(gazeIntervalRef.current);
    gazeIntervalRef.current = null;
  
    // Stop the webcam stream (this kills the green light)
    const video = document.querySelector('video');
    if (video && video.srcObject) {
      const stream = video.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      video.srcObject = null;
    }
  
    webgazer.pause();
    webgazer.end();
    webgazer.setGazeListener(null);
  
    webgazerInitialized.current = false;
    isGazeInsideRef.current = false;
  }, []);

  useEffect(() => {
    if (loading || !testId || webgazerInitialized.current) return;

    const initializeWebGazer = async () => {
      console.log("Initializing WebGazer...");

      try {

        await webgazer
          .setRegression('ridge')
          .setGazeListener((data) => {
            if (!data || !testWindowRef.current) {
              isGazeInsideRef.current = false;
              return;
            }

            const { left, right, top, bottom } = testWindowRef.current.getBoundingClientRect();
            const inside = data.x >= left && data.x <= right && data.y >= top && data.y <= bottom;

            isGazeInsideRef.current = inside;
            setIsGazeInside(inside);
          })
          .begin();

        const videoFeed = document.getElementById('webgazerVideoFeed');
          if (videoFeed) {
            videoFeed.style.position = 'fixed';  
            videoFeed.style.top = '0px';
            videoFeed.style.right = '0px'; 
            videoFeed.style.left = 'auto';  
            videoFeed.style.width = '200px';  
            videoFeed.style.height = '200px'; 
          }

        webgazer.showPredictionPoints(false);
        webgazer.showVideoPreview(true);  
        webgazer.showFaceOverlay(false);
        webgazer.showFaceFeedbackBox(false);

        webgazerInitialized.current = true;

        gazeIntervalRef.current = setInterval(() => {
          setFocusedTime((prev) => prev + (isGazeInsideRef.current ? 1 : 0));
          setDistractionTime((prev) => prev + (isGazeInsideRef.current ? 0 : 1));
        }, 1000);

        console.log("WebGazer initialized.");
      } catch (err) {
        console.error("WebGazer initialization failed:", err);
      }
    };

    initializeWebGazer();

    return () => stopWebGazer();
  }, [loading, testId, stopWebGazer]);

  const toggleVideoPreview = () => {
    setShowVideo((prev) => {
      const newShowVideo = !prev;

      const videoElem = document.getElementById('webgazerVideoFeed');
      if (videoElem) {
        videoElem.style.transition = 'opacity 0.5s ease';
        if (newShowVideo) {
          videoElem.style.display = 'block';
          setTimeout(() => {
            videoElem.style.opacity = '1';
          }, 10);
        } else {
          videoElem.style.opacity = '0';
          setTimeout(() => {
            videoElem.style.display = 'none';
          }, 500);
        }
      }

      return newShowVideo;
    });
  };

  const submithandle = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);

    stopWebGazer();

    logactivity(`Final Focused Time: ${focusedTime} seconds`);
    logactivity(`Final Distraction Time: ${distractionTime} seconds`);
    logactivity(`Submitted Test`, questions[questions.length - 1]?._id);

    try {
      const logs = JSON.parse(localStorage.getItem(`test_${testId}_logs`)) || [];
      const data = {
        userId,
        testId,
        centerId: localStorage.getItem('center_id'),
        logs,
        focusedTimeSeconds: focusedTime,
        distractionTimeSeconds: distractionTime,
      };
      //console.log(data);
      const res = await fetch(`${API_URL}/api/submitTest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      const responseData = await res.json();
      if (!res.ok) throw new Error('Failed to send logs');

      ["deadline", "selectedOptions", "logs", "teststarted"].forEach((key) =>
        localStorage.removeItem(`test_${testId}_${key}`)
      );

      setQuestions([]);
      setSelectedOptions([]);
      setTime(0);
      setCurrentQuestion(0);
      setFocusedTime(0);
      setDistractionTime(0);
      setIsGazeInside(false);

      await handleCompleteTest(testId, responseData.score);
      navigate('/Dashboard');
    } catch (err) {
      console.error("Submission error:", err);
      setIsSubmitting(false);
    }
  };

  const handleCompleteTest = (testId, score) => {
    const registered = JSON.parse(localStorage.getItem('registered_tests')) || [];
    const given = JSON.parse(localStorage.getItem('given_tests')) || [];

    const completedTest = registered.find(test => test._id === testId);
    if (completedTest) {
      localStorage.setItem(
        'registered_tests',
        JSON.stringify(registered.filter(test => test._id !== testId))
      );
      localStorage.setItem(
        'given_tests',
        JSON.stringify([...given, { ...completedTest, score }])
      );
    }
  };

  const handleOptionChange = useCallback((questionIndex, option) => {
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
  }, [selectedOptions, logactivity, questions, testId]);

  if (loading) return <div>Loading questions...</div>;

  return (
    <div className="test-window" id="test-window" ref={testWindowRef}>
      <DisableBackButton />
      <SidePanel
        questions={questions}
        currentQuestion={currentQuestion}
        onQuestionChange={handleQuestionChange}
        time={time}
        submithandle={submithandle}
        isSubmitting={isSubmitting}
        showVideo={showVideo}
        toggleVideoPreview={toggleVideoPreview}
      />
      <QuestionDisplay
        question={questions[currentQuestion]}
        currentQuestion={currentQuestion}
        totalQuestions={questions.length}
        selectedOption={selectedOptions[currentQuestion]}
        onOptionChange={(option) => handleOptionChange(currentQuestion, option)}
      />

      <div>

      </div>
    </div>
  );
};

export default TestWindow;

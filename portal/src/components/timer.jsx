import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from "react-router-dom";
import "../styles/timer.css";


const Timer = ({ time, submithandle }) => {
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const navigate = useNavigate();
  const deadline = useMemo(() => Date.now() + time, [time]);

  const getTime = useCallback(() => {
    const currentTime = Date.now();
    const timeDifference = deadline - currentTime;

    if (timeDifference >0) {
      setHours(Math.floor((timeDifference / (1000 * 60 * 60)) % 24));
      setMinutes(Math.floor((timeDifference / 1000 / 60) % 60));
      setSeconds(Math.floor((timeDifference / 1000) % 60));
    }

    else{
        submithandle();
        navigate('/Dashboard');
    }
  }, [deadline, navigate, submithandle]);

  useEffect(() => {
    const interval = setInterval(getTime, 1000);

    return () => clearInterval(interval);
  }, [getTime]);

  return (
    <div className="timer-container">
      <div className="timer-box">
        <p>{hours < 10 ? "0" + hours : hours}</p>
        <span>Hours</span>
      </div>
      <div className="timer-box">
        <p>{minutes < 10 ? "0" + minutes : minutes}</p>
        <span>Minutes</span>
      </div>
      <div className="timer-box">
        <p>{seconds < 10 ? "0" + seconds : seconds}</p>
        <span>Seconds</span>
      </div>
    </div>


  );
};

export default Timer;

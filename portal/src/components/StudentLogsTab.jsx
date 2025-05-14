import React, { useState, useEffect, useCallback } from "react";
import Dropdown from "./Dropdown";
import "../styles/StudentLogTab.css";

const StudentLogsTab = () => {
    const [studentId, setStudentId] = useState(null);
    const [testId, setTestId] = useState(null);
    const [logsData, setLogsData] = useState(null);
    const [tabSwitchCount, setTabSwitchCount] = useState(0);

    const [studentOptions, setStudentOptions] = useState([]);
    const [testOptions, setTestOptions] = useState([]);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

    const fetchStudents = useCallback(async () => {
        const cachedStudents = localStorage.getItem("students");
        if (cachedStudents) {
            setStudentOptions(JSON.parse(cachedStudents));
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/api/studentLog`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ studentId: null, testId: null }),
            });
            if (!response.ok) {
                throw new Error("Failed to fetch students");
            }
            const data = await response.json();
            
            if (Array.isArray(data.students)) {
                const formattedStudents = data.students.map((student) => ({
                    label: `${student.username} (${student.id})`,
                    value: student.id,
                }));
                setStudentOptions(formattedStudents);
                localStorage.setItem("students", JSON.stringify(formattedStudents));
            } else {
                throw new Error("Invalid response format for students");
            }
        } catch (err) {
            setError(err.message);
            setStudentOptions([]);
        } finally {
            setLoading(false);
        }
    }, [API_URL]);

    const fetchTests = useCallback(async (studentId) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/api/studentLog`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ studentId, testId: null }),
            });
            if (!response.ok) {
                throw new Error("Failed to fetch tests");
            }
            const data = await response.json();
            if (Array.isArray(data.tests)) {
                const formattedTests = data.tests.map(t => ({
                    label: t.test_name,
                    value: t.test_id
                }));
                setTestOptions(formattedTests);
            } else {
                throw new Error("Invalid response format for tests");
            }
        } catch (err) {
            setError(err.message);
            setTestOptions([]);
        } finally {
            setLoading(false);
        }
    }, [API_URL]);

    const fetchLogs = useCallback(async (studentId, testId) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/api/studentLog`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ studentId, testId }),
            });
            if (!response.ok) {
                throw new Error("Failed to fetch logs");
            }
            const data = await response.json();

            const logsArray = Array.isArray(data.logs) && data.logs.length > 0 ? data.logs[0].logs : null;
            let tabSwitchDurations = [];

            if (logsArray) {
                let lastTabSwitchTime = null;
                logsArray.forEach((log) => {
                    if (log && log.activity_text && log.activity_text.includes("Tab Switched")) {
                        lastTabSwitchTime = new Date(log.timestamp);
                    } else if (
                        log &&
                        log.activity_text &&
                        log.activity_text.includes("Returned to Test Tab") &&
                        lastTabSwitchTime
                    ) {
                        const returnedTime = new Date(log.timestamp);
                        const duration = (returnedTime - lastTabSwitchTime) / 1000; // Time in seconds
                        tabSwitchDurations.push(duration);
                        lastTabSwitchTime = null; // Reset for the next tab switch
                    }
                });
            }

            const totalTabSwitchTime = tabSwitchDurations.reduce((sum, time) => sum + time, 0);
            //console.log("Tab Switch Durations:", tabSwitchDurations); // Debugging
            //console.log("Total Tab Switch Time:", totalTabSwitchTime); // Debugging

            setTabSwitchCount(totalTabSwitchTime); // Total time spent during tab switches
            setLogsData(data);
        } catch (err) {
            setError(err.message);
            setLogsData(null);
        } finally {
            setLoading(false);
        }
    }, [API_URL]);

    useEffect(() => {
        fetchStudents();
    }, [fetchStudents]);

    useEffect(() => {
        if (studentId) {
            fetchTests(studentId);
            setTestId(null);
            setLogsData(null);
            setTabSwitchCount(0);
        } else {
            setTestOptions([]);
            setTestId(null);
            setLogsData(null);
            setTabSwitchCount(0);
        }
    }, [studentId, fetchTests]);

    useEffect(() => {
        if (studentId && testId) {
            fetchLogs(studentId, testId);
        } else {
            setLogsData(null);
            setTabSwitchCount(0);
        }
    }, [testId, fetchLogs, studentId]);

    const getActivityStyle = (activity) => {
        if (activity.includes("Tab Switched") || activity.includes("Returned to Test Tab")) {
            return "activity-tab-switch";
        }
        if (activity.includes("Test Started")) {
            return "activity-test-start";
        }
        if (activity.includes("Submitted Test")) {
            return "activity-test-submit";
        }
        return "activity-default";
    };

    const renderLogsContent = () => {
        if (loading) {
            return <div className="loading">Loading...</div>;
        }

        if (!loading && logsData && Array.isArray(logsData.logs) && logsData.logs.length > 0) {
            const activityLogs = logsData.logs[0].logs; // Access the logs array of the first log entry
            return (
                <div className="logs-container">
                    <div className="score-section">
                        <h3 className="sub-header">Test Score</h3>
                        <p className="score">
                            <strong>Score:</strong> {logsData.score}
                        </p>
                        {tabSwitchCount !== null && (
                            <p className="tab-switch">
                                <strong>Total Time in Tab Switches:</strong> {tabSwitchCount.toFixed(2)} seconds
                            </p>
                        )}
                    </div>
                    <div className="activity-section">
                        <h3 className="sub-header">Activity Logs</h3>
                        <ul className="activity-list">
                            {Array.isArray(activityLogs) && activityLogs.map((log, index) => (
                                <li
                                    key={index}
                                    className={`activity-item ${getActivityStyle(
                                        log.activity_text
                                    )}`}
                                >
                                    <div className="timestamp">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </div>
                                    <div className="activity-text">{log.activity_text}</div>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="time-section">
                        <h3 className="sub-header">Time Spent on Questions</h3>
                        <ul className="time-list">
                            {Array.isArray(logsData.logs[0].times) &&
                                logsData.logs[0].times.map((time, index) => (
                                    <li key={index} className="time-item">
                                        <div className="question-id">
                                            Question ID: <strong>{time.question_id}</strong>
                                        </div>
                                        <div className="time-spent">
                                            Time Spent: <strong>{time.time_spent.toFixed(2)}</strong> seconds
                                        </div>
                                    </li>
                                ))}
                        </ul>
                    </div>
                </div>
            );
        }

        if (!loading && !logsData && testId) {
            return <div className="no-logs">No logs available for this test.</div>;
        }

        return null;
    };

    return (
        <div className="student-logs-tab">
            <h2 className="header">Student Logs</h2>
            {error && <div className="error-message">Error: {error}</div>}
            <div className="dropdowns">
                <Dropdown
                    label="Select Student"
                    options={studentOptions}
                    value={studentId || ""}
                    onChange={(value) => setStudentId(value || null)}
                />
                {studentId && (
                    <Dropdown
                        label="Select Test"
                        options={testOptions}
                        value={testId || ""}
                        onChange={(value) => setTestId(value || null)}
                    />
                )}
            </div>
            {renderLogsContent()}
        </div>
    );
};

export default StudentLogsTab;

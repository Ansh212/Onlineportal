import React, { useState, useEffect, useCallback } from "react";
import Dropdown from "./Dropdown";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const FlaggedResultsTab = () => {
    const [testId, setTestId] = useState(null);
    const [flaggedData, setFlaggedData] = useState(null);

    const [testOptions, setTestOptions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

    const fetchTestOptions = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const userId = localStorage.getItem("userid");
            if (!userId) {
                throw new Error("User ID not found in localStorage");
            }

            const response = await fetch(`${API_URL}/api/get_tests`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ userId }),
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch test options: ${response.statusText}`);
            }

            const data = await response.json();
            if (data && Array.isArray(data.tests)) {
                setTestOptions(
                    data.tests.map((test) => ({
                        label: test.name,
                        value: test._id,
                    }))
                );
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

    const fetchFlaggedResults = useCallback(async (testId) => {
        setLoading(true);
        setError(null);
        try {
            const userId = localStorage.getItem("userid");
            if (!userId) {
                throw new Error("User ID not found in localStorage");
            }

            const response = await fetch(`${API_URL}/api/evaluate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ userId, testId }),
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch flagged results: ${response.statusText}`);
            }

            const data = await response.json();
            data.flagged_users = data.flagged_users.sort((a, b) => {
                const numA = parseInt(a.username.replace(/\D/g, ''), 10); // extract numbers
                const numB = parseInt(b.username.replace(/\D/g, ''), 10);
                return numA - numB;
            });
            setFlaggedData(data);
        } catch (err) {
            setError(err.message);
            setFlaggedData(null);
        } finally {
            setLoading(false);
        }
    }, [API_URL]);

    useEffect(() => {
        fetchTestOptions();
    }, [fetchTestOptions]);

    useEffect(() => {
        if (testId) {
            fetchFlaggedResults(testId);
        } else {
            setFlaggedData(null);
        }
    }, [testId, fetchFlaggedResults]);

    const renderCharts = () => {
        if (!flaggedData || !flaggedData.summary) return null;
    
        const {
            total_registered = 0,
            total_given = 0,
            total_not_given = 0,
            total_flagged = 0,
        } = flaggedData.summary;
    
        // Data for the first chart (Flagged vs Non-Flagged)
        const flaggedDataChart = {
            labels: ["Flagged", "Not Flagged"],
            datasets: [
                {
                    data: [total_flagged, total_given - total_flagged],
                    backgroundColor: ["#FF6384", "#36A2EB"],
                    hoverBackgroundColor: ["#FF638490", "#36A2EB90"],
                },
            ],
        };
    
        // Data for the second chart (Given vs Not Given)
        const registrationDataChart = {
            labels: ["Given Tests", "Not Given Tests"],
            datasets: [
                {
                    data: [total_given, total_not_given],
                    backgroundColor: ["#4BC0C0", "#FFCE56"],
                    hoverBackgroundColor: ["#4BC0C090", "#FFCE5690"],
                },
            ],
        };
    
        return (
            <div
                className="chart-container"
                style={{
                    display: "flex",
                    gap: "20px",
                    flexWrap: "wrap",
                    marginBottom: "40px", // Adds space between charts and the lists below
                }}
            >
                <div
                    className="chart-card"
                    style={{
                        flex: "1 1 calc(50% - 20px)",
                        maxWidth: "calc(50% - 20px)",
                        padding: "20px",
                        border: "1px solid #ddd",
                        borderRadius: "8px",
                        backgroundColor: "#f9f9f9",
                        boxSizing: "border-box",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                    }}
                >
                    <h4>Flagged vs Non-Flagged</h4>
                    <div style={{ maxWidth: "100%", height: "300px" }}>
                        <Pie data={flaggedDataChart} />
                    </div>
                    <p>Total Registered Students: <strong>{total_registered}</strong></p>
                </div>
                <div
                    className="chart-card"
                    style={{
                        flex: "1 1 calc(50% - 20px)",
                        maxWidth: "calc(50% - 20px)",
                        padding: "20px",
                        border: "1px solid #ddd",
                        borderRadius: "8px",
                        backgroundColor: "#f9f9f9",
                        boxSizing: "border-box",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                    }}
                >
                    <h4>Given vs Not Given</h4>
                    <div style={{ maxWidth: "100%", height: "300px" }}>
                        <Pie data={registrationDataChart} />
                    </div>
                    <p>Total Registered Students: <strong>{total_registered}</strong></p>
                </div>
            </div>
        );
    };
    
    const renderFlaggedUsersAndCenters = () => {
        return (
            <div
                className="list-container"
                style={{
                    display: "flex",
                    gap: "20px",
                    flexWrap: "wrap",
                }}
            >
                <div
                    style={{
                        flex: "1 1 calc(50% - 20px)",
                        maxWidth: "calc(50% - 20px)",
                        padding: "20px",
                        border: "1px solid #ddd",
                        borderRadius: "8px",
                        backgroundColor: "#f9f9f9",
                        boxSizing: "border-box",
                    }}
                >
                    <h3 className="sub-header">Flagged Users</h3>
                    <ul className="activity-list">
                        {flaggedData && flaggedData.flagged_users.length > 0
                            ? flaggedData.flagged_users.map((user, index) => (
                                  <li key={index} className="activity-item activity-default">
                                      <div className="activity-text">
                                          {user.username} ({user._id})
                                      </div>
                                  </li>
                              ))
                            : <li className="activity-item activity-default">No flagged users</li>}
                    </ul>
                </div>
                <div
                    style={{
                        flex: "1 1 calc(50% - 20px)",
                        maxWidth: "calc(50% - 20px)",
                        padding: "20px",
                        border: "1px solid #ddd",
                        borderRadius: "8px",
                        backgroundColor: "#f9f9f9",
                        boxSizing: "border-box",
                    }}
                >
                    <h3 className="sub-header">Flagged Centers</h3>
                    <ul className="activity-list">
                        {flaggedData && flaggedData.flagged_centers.length > 0
                            ? flaggedData.flagged_centers.map((centerId, index) => (
                                  <li key={index} className="activity-item activity-default">
                                      <div className="activity-text">
                                          Center ID: <strong>{centerId}</strong>
                                      </div>
                                  </li>
                              ))
                            : <li className="activity-item activity-default">No flagged centers</li>}
                    </ul>
                </div>
            </div>
        );
    };
    
    return (
        <div className="student-logs-tab">
            <h2 className="header">Flagged Results</h2>
            {error && <div className="error-message">Error: {error}</div>}
    
            <div className="dropdowns">
                <Dropdown
                    label="Select Test"
                    options={testOptions}
                    value={testId || ""}
                    onChange={(value) => setTestId(value || null)}
                />
            </div>
    
            {loading && <div className="loading">Loading...</div>}
    
            {!loading && flaggedData && (
                <>
                    <div className="logs-container">
                        <div className="score-section">
                            {renderCharts()}
                            {renderFlaggedUsersAndCenters()}
                        </div>
                    </div>
                </>
            )}
    
            {!loading && !flaggedData && testId && (
                <div className="no-logs">No flagged results available for this test.</div>
            )}
    
            {!loading && !testId && <div className="no-logs">Please select a test to view results.</div>}
        </div>
    );
    
};

export default FlaggedResultsTab;

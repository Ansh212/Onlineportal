import React, { useState, useEffect, useCallback } from "react";
import { Bar } from "react-chartjs-2";
import Dropdown from "./Dropdown";
import "../styles/AvgScore.css";

const AvgScoreTab = () => {
    const [testOptions, setTestOptions] = useState([]);
    const [testId, setTestId] = useState(null);
    const [stateName, setStateName] = useState(null);
    const [cityName, setCityName] = useState(null);

    const [stateOptions, setStateOptions] = useState([]);
    const [cityOptions, setCityOptions] = useState([]);
    const [chartData, setChartData] = useState(null);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const userid = localStorage.getItem("userid");
    const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

    const prepareChartData = useCallback((data, level) => {
        const labelKey =
            level === "state" ? "state" : level === "city" ? "city" : "center_id";

        setChartData({
            labels: data.map((item) => item[labelKey]),
            datasets: [
                {
                    label: `Average Score by ${capitalizeFirstLetter(level)}`,
                    data: data.map((item) => item.avg_score),
                    backgroundColor: "rgba(75, 192, 192, 0.6)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 1,
                },
            ],
        });
    }, []);

    const capitalizeFirstLetter = (string) =>
        string.charAt(0).toUpperCase() + string.slice(1);

    const fetchTests = useCallback(async () => {
        const cachedTests = localStorage.getItem("tests");
        if (cachedTests) {
            setTestOptions(JSON.parse(cachedTests));
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/api/get_tests`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ userId: userid }),
            });
            if (!response.ok) {
                throw new Error("Failed to fetch tests");
            }
            const data = await response.json();

            if (data && Array.isArray(data.tests)) {
                const formattedTests = data.tests.map((test) => ({
                    label: test.name,
                    value: test._id,
                }));
                setTestOptions(formattedTests);
                localStorage.setItem("tests", JSON.stringify(formattedTests));
            } else {
                throw new Error("Invalid response format");
            }            
        } catch (err) {
            setError(err.message);
            setTestOptions([]);
        } finally {
            setLoading(false);
        }
    }, [API_BASE_URL, userid]);

    const fetchStates = useCallback(
        async (testId) => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/api/avgScore`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ testId: testId, state: null, city: null }),
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch states");
                }
                const data = await response.json();

                if (Array.isArray(data.data)) {
                    setStateOptions(
                        data.data.map((state) => ({
                            label: state.state,
                            value: state.state,
                        }))
                    );
                    prepareChartData(data.data, "state");
                } else {
                    throw new Error("Invalid response format for states");
                }
            } catch (err) {
                setError(err.message);
                setStateOptions([]);
                setChartData(null);
            } finally {
                setLoading(false);
            }
        },
        [API_BASE_URL, prepareChartData]
    );

    const fetchCities = useCallback(
        async (testId, stateName) => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/api/avgScore`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ testId: testId, state: stateName, city: null }),
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch cities");
                }
                const data = await response.json();

                if (Array.isArray(data.data)) {
                    setCityOptions(
                        data.data.map((city) => ({
                            label: city.city,
                            value: city.city,
                        }))
                    );
                    prepareChartData(data.data, "city");
                } else {
                    throw new Error("Invalid response format for cities");
                }
            } catch (err) {
                setError(err.message);
                setCityOptions([]);
                setChartData(null);
            } finally {
                setLoading(false);
            }
        },
        [API_BASE_URL, prepareChartData]
    );

    const fetchCenters = useCallback(
        async (testId, stateName, cityName) => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/api/avgScore`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ testId, state: stateName, city: cityName }),
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch centers");
                }
                const data = await response.json();

                if (Array.isArray(data.data)) {
                    prepareChartData(data.data, "center");
                } else {
                    throw new Error("Invalid response format for centers");
                }
            } catch (err) {
                setError(err.message);
                setChartData(null);
            } finally {
                setLoading(false);
            }
        },
        [API_BASE_URL, prepareChartData]
    );

    useEffect(() => {
        fetchTests();
    }, [fetchTests]);

    useEffect(() => {
        if (testId) {
            setStateName(null);
            setCityName(null);
            fetchStates(testId);
        } else {
            setStateOptions([]);
            setStateName(null);
            setCityName(null);
            setChartData(null);
        }
    }, [testId, fetchStates]);

    useEffect(() => {
        if (stateName) {
            setCityName(null);
            fetchCities(testId, stateName);
        } else if (testId) {
            fetchStates(testId);
        }
    }, [stateName, fetchCities, fetchStates, testId]);

    useEffect(() => {
        if (cityName) {
            fetchCenters(testId, stateName, cityName);
        } else if (stateName) {
            fetchCities(testId, stateName);
        }
    }, [cityName, fetchCenters, fetchCities, stateName, testId]);

    return (
        <div className="avg-score-tab">
            <h2 className="header">Average Score Analysis</h2>
            {error && <div className="error-message">Error: {error}</div>}
            <div className="dropdowns">
                <Dropdown
                    label="Select Test"
                    options={testOptions}
                    value={testId || ""}
                    onChange={(value) => setTestId(value || null)}
                />
                {testId && (
                    <Dropdown
                        label="Select State"
                        options={stateOptions}
                        value={stateName || ""}
                        onChange={(value) => setStateName(value || null)}
                    />
                )}
                {stateName && (
                    <Dropdown
                        label="Select City"
                        options={cityOptions}
                        value={cityName || ""}
                        onChange={(value) => setCityName(value || null)}
                    />
                )}
            </div>
            {loading ? (
                <div className="loading">Loading...</div>
            ) : chartData ? (
                <div className="chart-container">
                    <Bar
                        data={chartData}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: "Location",
                                    },
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: "Average Score",
                                    },
                                    beginAtZero: true,
                                },
                            },
                        }}
                    />
                </div>
            ) : (
                <div className="no-data">No data available</div>
            )}
        </div>
    );
};

export default AvgScoreTab;


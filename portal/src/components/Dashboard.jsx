import React, { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';
import Popup from 'reactjs-popup';
import 'reactjs-popup/dist/index.css';
import '../styles/Dashboard.css'; 
import TestDetailsForm from './TestDetailsForm'; 

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

const Dashboard = ({ onLogout }) => {
    const [tab, setTab] = useState("available");
    const [availableTests, setAvailableTests] = useState([]);
    const [registeredTests, setRegisteredTests] = useState(() => {
        const storedTests = localStorage.getItem('registered_tests');
        return storedTests ? JSON.parse(storedTests) : [];
    });
    const [givenTests, setGivenTests] = useState(() => {
        const storedTests = localStorage.getItem('given_tests');
        return storedTests ? JSON.parse(storedTests) : [];
    });
    const [isLoading, setIsLoading] = useState(true);
    const [showTestForm, setShowTestForm] = useState(false);
    const [selectedTestId, setSelectedTestId] = useState(null);
    const navigate = useNavigate();
    const userid = localStorage.getItem('userid');

    const handleLogoutTotal = () => {
        onLogout();
        navigate('/');
    };
    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const response = await fetch(`${API_URL}/api/get_tests`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ userId: userid }),
                });
                const data = await response.json()
                ;
                if (data.tests && Array.isArray(data.tests)) {
                    setAvailableTests(data.tests);
                } else {
                    console.error("Expected an array of tests, but received:", data);
                    setAvailableTests([]); // Fallback to an empty array
                }
                setIsLoading(false);
            } catch (error) {
                console.log(error);
                setIsLoading(false);
            }
        };
        if (tab === "available") {
            fetchDashboard();
        }
    }, [tab, userid]);

    const handleEnroll = async (testId) => {
        try {
            const response = await fetch(`${API_URL}/api/enroll`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userId: userid,
                    testId: testId,
                }),
            });
    
            const data = await response.json();
            
            if (response.ok) {
                alert(data.message || 'Enrolled successfully!');
                
                const { registered_test } = data;
                //console.log(data);
                const updatedRegisteredTests = Array.isArray(registeredTests) ? [...registeredTests, registered_test] : [registered_test];
                setAvailableTests(availableTests.filter(test => test._id !== testId));
                setRegisteredTests(updatedRegisteredTests);
                localStorage.setItem('registered_tests', JSON.stringify(updatedRegisteredTests));
                //console.log(updatedRegisteredTests);
            } else {
                alert(data.message || 'Failed to enroll.');
            }
        } catch (error) {
            console.error('Error enrolling in test:', error);
        }
    };

    const handleTakeTest = async (testId, center_id) => {

        try {
            const response = await fetch(`${API_URL}/api/take_test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userId: userid, testId: testId }),
            });
      
            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.message || 'Test is not yet available.');
                return;
            }
      
            localStorage.setItem('center_id', center_id);
            setSelectedTestId(testId);
            setShowTestForm(true);
        } catch (error) {
            console.error('Error checking test availability:', error);
            alert('An error occurred while trying to start the test. Please try again.');
        }
    };
 
    const handleSubmitTestDetails = () => {
        navigate(`/TestWindow/${selectedTestId}`);
        const updatedGivenTests = JSON.parse(localStorage.getItem('given_tests')) || [];
        setGivenTests(updatedGivenTests);

        const updatedRegisteredTests = JSON.parse(localStorage.getItem('registered_tests')) || [];
        setRegisteredTests(updatedRegisteredTests); // Correctly update registered tests

        //console.log(givenTests);
        //console.log(registeredTests);
    };

    const handleCancelTest = () => {
        setShowTestForm(false); 
        setSelectedTestId(null); 
    };

    if (isLoading) {
        return <div>Loading your Dashboard...</div>;
    }

    //console.log(registeredTests);
    // console.log(availableTests);
    //console.log(givenTests);

    return (
        <div className="dashboard-container">
            <h1 className="dashboard-heading">Student Dashboard</h1>
            <button onClick={handleLogoutTotal} className="logout-button">Logout</button>

            <div className="tab-buttons">
                <button onClick={() => setTab("available")} className={tab === "available" ? "active-tab" : ""}>
                    Available Tests
                </button>
                <button onClick={() => setTab("registered")} className={tab === "registered" ? "active-tab" : ""}>
                    Registered Tests
                </button>
                <button onClick={() => setTab("given")} className={tab === "given" ? "active-tab" : ""}>
                    Given Tests
                </button>
            </div>

            {tab === "available" && (
                <div>
                    <h2 className="sub-heading">Available Tests</h2>
                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th className="table-header">Test Name</th>
                                <th className="table-header">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {availableTests.map((test) => (
                                <tr key={test._id}>
                                    <td className="table-cell">{test.name}</td>
                                    <td className="table-cell">
                                        <button className="enroll-button" onClick={() => handleEnroll(test._id)}>Enroll</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {tab === "registered" && (
                <div>
                    <h2 className="sub-heading">Registered Tests</h2>
                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th className="table-header">Test Name</th>
                                <th className="table-header">City</th>
                                <th className="table-header">State</th>
                                <th className="table-header">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(registeredTests || []).map((test, index) => (
                                <tr key={index}>
                                    <td className="table-cell">{test.test_name}</td>
                                    <td className="table-cell">{test.city}</td>
                                    <td className="table-cell">{test.state}</td>
                                    <td className="table-cell">
                                        <button className="take-test-button" onClick={() => handleTakeTest(test._id, test.center_id)}>Take Test</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {tab === "given" && (
                <div>
                    <h2 className="sub-heading">Given Tests</h2>
                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th className="table-header">Test Name</th>
                                <th className="table-header">Score</th>
                                <th className="table-header">City</th>
                                <th className="table-header">State</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(givenTests || []).map((test, index) => (
                                <tr key={index}>
                                    <td className="table-cell">{test.test_name}</td>
                                    <td className="table-cell">{test.score}</td>
                                    <td className="table-cell">{test.city}</td>
                                    <td className="table-cell">{test.state}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {showTestForm && (
                <Popup open={showTestForm} modal closeOnDocumentClick={false}>
                    <TestDetailsForm onSubmit={handleSubmitTestDetails} onCancel={handleCancelTest} />
                </Popup>
            )}
        </div>
    );
};

export default Dashboard;

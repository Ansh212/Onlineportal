import React, { useState } from "react";
import AvgScoreTab from "./AvgScoreTab";
import AvgTimeTab from "./AvgTimeTab";
import StudentLogsTab from "./StudentLogsTab";
import FlaggedResultTab from "./FlaggedResultTab"; // Import the new tab
import { useNavigate } from "react-router-dom";
import "../styles/AdminDashboard.css";

const AdminDashboard = ({ onLogout }) => {
    const [activeTab, setActiveTab] = useState("avgScore");
    const navigate = useNavigate();

    const handleLogoutTotal = () => {
        onLogout();
        localStorage.removeItem("tests");
        localStorage.removeItem("students");
        navigate("/");
    };

    return (
        <div className="admin-dashboard">
            <h1>Admin Dashboard</h1>

            <button onClick={handleLogoutTotal} className="logout-button">
                Logout
            </button>

            {/* Tabs */}
            <div className="tab-buttons">
                <button
                    onClick={() => setActiveTab("avgScore")}
                    className={activeTab === "avgScore" ? "active-tab" : ""}
                >
                    Average Score
                </button>
                <button
                    onClick={() => setActiveTab("avgTime")}
                    className={activeTab === "avgTime" ? "active-tab" : ""}
                >
                    Average Time
                </button>
                <button
                    onClick={() => setActiveTab("studentLogs")}
                    className={activeTab === "studentLogs" ? "active-tab" : ""}
                >
                    Student Logs
                </button>
                <button
                    onClick={() => setActiveTab("flaggedResults")}
                    className={activeTab === "flaggedResults" ? "active-tab" : ""}
                >
                    Flagged Results
                </button>
            </div>

            {/* Tab Content */}
            {activeTab === "avgScore" && <AvgScoreTab />}
            {activeTab === "avgTime" && <AvgTimeTab />}
            {activeTab === "studentLogs" && <StudentLogsTab />}
            {activeTab === "flaggedResults" && <FlaggedResultTab />}
        </div>
    );
};

export default AdminDashboard;

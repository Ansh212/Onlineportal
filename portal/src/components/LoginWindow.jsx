import React, { useState } from "react";
import "../login.css";
import { useNavigate } from "react-router-dom";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000"; 

const LoginWindow = ({ onlogin }) => {
    const [Username, setUsername] = useState('');
    const [Password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (event) => {
        event.preventDefault();
    
        if (!Username || !Password) {
            alert('Username and Password are required.');
            return;
        }
    
        try {
            const response = await fetch(`${API_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: Username,
                    password: Password,
                }),
            });
    
            const data = await response.json();
    
            if (!response.ok) {
                alert(data.message || 'Login failed. Please try again.');
            } else {
                if (!data || !data.data) {
                    alert('Unexpected response from the server.');
                    return;
                }
    
                const user = data.data;
    
                // Store individual properties from the object response
                localStorage.setItem('userid', user.id || ''); // User ID
                localStorage.setItem('username', user.username || ''); // Username
                localStorage.setItem('role', user.role || ''); // Role (can be null or 'admin')
                localStorage.setItem('registered_tests', JSON.stringify(user.registered_tests || [])); // Registered tests array
                localStorage.setItem('given_tests', JSON.stringify(user.given_tests || [])); // Given tests array
    
                // console.log(localStorage.getItem('userid')); // Debugging
                // console.log(localStorage.getItem('registered_tests')); // Debugging
    
                // Navigate based on role
                if (user.role === 'admin') {
                    navigate('/AdminDashboard');
                } else {
                    navigate('/Dashboard');
                }
    
                onlogin();
            }
        } catch (error) {
            console.error('Error logging in:', error);
            alert('An error occurred while trying to log in. Please try again.');
        }
    };
    

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Login</h2>
                <form onSubmit={handleLogin}>
                    <div className="input-group">
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            placeholder="Enter your username"
                            value={Username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div className="input-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            placeholder="Enter your password"
                            value={Password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <button type="submit" className="login-btn">
                        Login
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginWindow;

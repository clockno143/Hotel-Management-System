import React, { useState } from "react";
import { InputText } from 'primereact/inputtext';
import { Button } from "primereact/button";
import { signin, signup } from "./service/userapi";

export function USserLogin({ setToken, setRole }) {
    const [username, setUsername] = useState('');  // Fix typo and initialize state
    const [password, setPassword] = useState('');  // Initialize with empty string

    const signInCall = async () => {
        let req = {
            "username": username,   // Fixed typo here
            "password": password,
        };

        try {
            let response = await signin(req);
            console.log(response);
            setRole(response['role']);
            setToken(response['token']);
        } catch (error) {  // Lowercase error
            alert("Error Occurred" + error);
        }
    };

    const signupCall = async () => {
        let req = {
            "username": username,   // Fixed typo here
            "password": password,
        };

        try {
            let response = await signup(req);
            alert(response.message);
        } catch (error) {  // Lowercase error
            alert("Error Occurred");
        }
    };

    return (
        <div>
            <div className="input-group" style={{ marginBottom: '15px' }}>
                <label
                    htmlFor="username"
                    style={{
                        display: 'block',
                        fontSize: '14px',
                        color: '#333',
                        marginBottom: '5px',
                    }}
                >
                    Username
                </label>
                <InputText
                    value={username}   // Fixed variable name
                    placeholder="Username"
                    onChange={(e) => setUsername(e.target.value)}   // Fixed variable name
                    style={{
                        width: '100%',
                        padding: '10px',
                        border: '1px solid #ccc',
                        borderRadius: '4px',
                        fontSize: '14px',
                    }}
                />
            </div>

            <div className="input-group" style={{ marginBottom: '20px' }}>
                <label
                    htmlFor="password"
                    style={{
                        display: 'block',
                        fontSize: '14px',
                        color: '#333',
                        marginBottom: '5px',
                    }}
                >
                    Password
                </label>
                <InputText
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{
                        width: '100%',
                        padding: '10px',
                        border: '1px solid #ccc',
                        borderRadius: '4px',
                        fontSize: '14px',
                    }}
                />
            </div>

            <div
                className="button-group"
                style={{
                    display: 'flex',
                    justifyContent: 'center',
                    gap: '20px',
                    marginTop: '20px',
                }}
            >
                <Button
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '16px',
                        transition: 'background-color 0.3s',
                    }}
                    onClick={signInCall}
                >
                    Sign In
                </Button>
                <Button
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#2196F3',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '16px',
                        transition: 'background-color 0.3s',
                    }}
                    onClick={signupCall}   // Fixed function name
                >
                    Sign Up
                </Button>
            </div>
        </div>
    );
}

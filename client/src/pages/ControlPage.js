/**
 * This file defines the ControlPage component, which provides functionality for managing groups and users.
 * It includes forms for creating new groups and users, and sends the data to the backend API.
 */


import React, { useState } from "react";
import API from "../api";

/**
 * ControlPage component for managing groups and users.
 * Provides forms for creating new groups and users.
 */
function ControlPage() {
    /**
     * State variables to manage input fields for creating groups and users.
     */
    const [newGroupName, setNewGroupName] = useState("");
    const [newUserName, setNewUserName] = useState("");
    const [newUserEmail, setNewUserEmail] = useState("");
    const [newUserPassword, setNewUserPassword] = useState("");

    /**
     * Handles the creation of a new group.
     * Validates the group name and sends a POST request to the backend to create the group.
     * Clears the input field and alerts the user on success.
     */
    const handleCreateGroup = () => {
        if (!newGroupName.trim()) {
            alert("Group name is required.");
            return;
        }
        API.post("/groups/", { name: newGroupName })
            .then(() => {
                alert("Group created successfully!");
                setNewGroupName("");
            })
            .catch((error) => console.error("Error creating group:", error));
    };

    /**
     * Handles the creation of a new user.
     * Validates the user fields (name, email, password) and sends a POST request to the backend to create the user.
     * Clears the input fields and alerts the user on success.
     */
    const handleCreateUser = () => {
        if (!newUserName.trim() || !newUserEmail.trim() || !newUserPassword.trim()) {
            alert("All user fields are required.");
            return;
        }
        API.post("/users/", {
            name: newUserName,
            email: newUserEmail,
            password: newUserPassword,
        })
            .then(() => {
                alert("User created successfully!");
                setNewUserName("");
                setNewUserEmail("");
                setNewUserPassword("");
            })
            .catch((error) => console.error("Error creating user:", error));
    };

    return (
        <div className="control-page">
            <h2>Control Page</h2>
            {/* Section for creating a new group */}
            <div>
                <h3>Create New Group</h3>
                <input
                    type="text"
                    placeholder="Group Name"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                />
                <button onClick={handleCreateGroup}>Create Group</button>
            </div>

            {/* Section for creating a new user */}
            <div>
                <h3>Create New User</h3>
                <input
                    type="text"
                    placeholder="User Name"
                    value={newUserName}
                    onChange={(e) => setNewUserName(e.target.value)}
                />
                <input
                    type="email"
                    placeholder="User Email"
                    value={newUserEmail}
                    onChange={(e) => setNewUserEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="User Password"
                    value={newUserPassword}
                    onChange={(e) => setNewUserPassword(e.target.value)}
                />
                <button onClick={handleCreateUser}>Create User</button>
            </div>
        </div>
    );
}

export default ControlPage;
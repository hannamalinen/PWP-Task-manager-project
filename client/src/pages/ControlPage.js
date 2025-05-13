/**
 * This file defines the ControlPage component, which provides functionality for managing groups and users.
 * It includes forms for creating new groups and users, and sends the data to the backend API.
 */

import React, { useState } from "react";
import API from "../api";
import "./ControlPage.css"; // Add CSS for styling the modal

/**
 * ControlPage component for managing groups and users.
 * Provides forms for creating new groups and users, and a button to view all users in a modal.
 */
function ControlPage() {
    /**
     * State variables to manage input fields for creating groups and users.
     */
    const [newGroupName, setNewGroupName] = useState("");
    const [newUserName, setNewUserName] = useState("");
    const [newUserEmail, setNewUserEmail] = useState("");
    const [newUserPassword, setNewUserPassword] = useState("");
    const [users, setUsers] = useState([]); // State to store the list of users
    const [isModalOpen, setIsModalOpen] = useState(false); // State to toggle modal visibility

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
            .then((response) => {
                const createdUser = response.data;
                console.log("User created successfully:", createdUser);
                console.log("Unique User ID:", createdUser.unique_user); // Log the unique_user ID
                alert("User created successfully!");
                setNewUserName("");
                setNewUserEmail("");
                setNewUserPassword("");
            })
            .catch((error) => console.error("Error creating user:", error.response?.data || error.message));
    };

    /**
     * Handles fetching and displaying the list of users.
     * Sends a GET request to the backend to fetch the users and updates the state.
     */
    const handleViewUsers = () => {
        API.get("/users/")
            .then((response) => {
                setUsers(response.data); // Store the fetched users in state
                setIsModalOpen(true); // Open the modal
            })
            .catch((error) => console.error("Error fetching users:", error));
    };

    /**
     * Handles deleting a user.
     * Sends a DELETE request to the backend to delete the user and updates the state.
     */
    const handleDeleteUser = (uniqueUserId) => {
        if (!window.confirm("Are you sure you want to delete this user?")) return;

        API.delete(`/users/${uniqueUserId}/`) // Use uniqueUserId here
            .then(() => {
                // Remove the deleted user from the state
                setUsers((prevUsers) => prevUsers.filter((user) => user.unique_user !== uniqueUserId));
                alert("User deleted successfully!");
            })
            .catch((error) => console.error("Error deleting user:", error));
    };

    /**
     * Handles closing the modal.
     */
    const handleCloseModal = () => {
        setIsModalOpen(false); // Close the modal
    };

    return (
        <div className="control-page">
            <h2>Control Page</h2>

            {/* Section for creating a new group */}
            <div className="form-section">
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
            <div className="form-section">
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

            {/* Button to view all users */}
            <div className="form-section">
                <h3>View All Users</h3>
                <button onClick={handleViewUsers}>View Users</button>
            </div>

            {/* Modal for displaying the user list */}
            {isModalOpen && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>All Users</h3>
                        <button className="close-button" onClick={handleCloseModal}>
                            Close
                        </button>
                        {users.length > 0 ? (
                            <table className="user-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {users.map((user) => (
                                        <tr key={user.unique_user}>
                                            <td>{user.name}</td>
                                            <td>{user.email}</td>
                                            <td>
                                                <button
                                                    className="delete-button"
                                                    onClick={() => handleDeleteUser(user.unique_user)} // Pass unique_user here
                                                >
                                                    🗑️
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <p>No users found.</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default ControlPage;
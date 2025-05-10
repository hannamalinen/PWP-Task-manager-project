// This file is responsible for managing the users in a group.
// it includes functionality to create new users, assign them to a group, and 
// remove them from a group.

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types"; // Import PropTypes
import API from "../api";
import "./UsersPanel.css"; // Add CSS for styling

function UsersPanel({ groupId }) {
    const [users, setUsers] = useState([]);
    const [allUsers, setAllUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null); // Track the selected user
    const [newUserName, setNewUserName] = useState("");
    const [newUserEmail, setNewUserEmail] = useState("");
    const [newUserPassword, setNewUserPassword] = useState("");
    const [selectedUserId, setSelectedUserId] = useState("");
    const [selectedRole, setSelectedRole] = useState("member"); // Default role is "member"

    useEffect(() => {
        if (groupId) {
            API.get(`/groups/${groupId}/members/`)
                .then((response) => setUsers(response.data || []))
                .catch((error) => console.error("Error fetching users:", error));

            API.get("/users/")
                .then((response) => setAllUsers(response.data || []))
                .catch((error) => console.error("Error fetching all users:", error));
        }
    }, [groupId]);

    const handleAddUser = () => {
        if (!newUserName.trim()) {
            alert("User name is required.");
            return;
        }
        if (!newUserEmail.trim()) {
            alert("User email is required.");
            return;
        }
        if (!newUserPassword.trim()) {
            alert("User password is required.");
            return;
        }

        const payload = {
            name: newUserName,
            email: newUserEmail,
            password: newUserPassword,
        };

        API.post("/users/", payload)
            .then((response) => {
                setAllUsers((prevUsers) => [...prevUsers, response.data]);
                setNewUserName("");
                setNewUserEmail("");
                setNewUserPassword("");
            })
            .catch((error) => {
                console.error("Error creating user:", error.response?.data || error.message);
                alert(error.response?.data?.error || "Failed to create user. Please try again.");
            });
    };

    const handleAssignUserToGroup = () => {
        if (!selectedUserId) {
            alert("Please select a user to assign to the group.");
            return;
        }

        const payload = { user_id: selectedUserId, role: selectedRole };

        API.post(`/groups/${groupId}/user/`, payload)
            .then((response) => {
                setUsers((prevUsers) => [...prevUsers, response.data]);
                setSelectedUserId("");
                setSelectedRole("member");
            })
            .catch((error) => {
                console.error("Error assigning user to group:", error.response?.data || error.message);
                alert(error.response?.data?.error || "Failed to assign user to group. Please try again.");
            });
    };

    const handleRemoveUserFromGroup = (userId) => {
        if (!window.confirm("Are you sure you want to remove this user from the group?")) return;

        API.delete(`/groups/${groupId}/user/`, {
            data: { user_id: userId },
        })
            .then(() => {
                setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));
                setSelectedUser(null); // Close the modal after removal
            })
            .catch((error) => console.error("Error removing user from group:", error));
    };

    const handleUserClick = (user) => {
        setSelectedUser(user); // Set the clicked user as the selected user
    };

    const handleCloseDetails = () => {
        setSelectedUser(null); // Clear the selected user
    };

    return (
        <div className="users-panel">
            <h2>Users in Group</h2>
            <ul className="user-list">
                {users.map((user) => (
                    <li
                        key={user.id}
                        className="user-item"
                        onClick={() => handleUserClick(user)} // Handle user click
                    >
                        <span className="user-name">{user.name}</span>
                        <span className="user-role">{user.role}</span>
                    </li>
                ))}
            </ul>

            {/* User Details Modal */}
            {selectedUser && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>User Details</h3>
                        <p><strong>Name:</strong> {selectedUser.name}</p>
                        <p><strong>Email:</strong> {selectedUser.email}</p>
                        <p><strong>Role:</strong> {selectedUser.role}</p>
                        <button
                            className="delete-button"
                            onClick={() => handleRemoveUserFromGroup(selectedUser.id)}
                        >
                            Remove User from Group
                        </button>
                        <button className="close-button" onClick={handleCloseDetails}>
                            Close
                        </button>
                    </div>
                </div>
            )}

            <div className="add-user">
                <h3>Create New User</h3>
                <input
                    type="text"
                    placeholder="New User Name"
                    value={newUserName}
                    onChange={(e) => setNewUserName(e.target.value)}
                />
                <input
                    type="email"
                    placeholder="New User Email"
                    value={newUserEmail}
                    onChange={(e) => setNewUserEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="New User Password"
                    value={newUserPassword}
                    onChange={(e) => setNewUserPassword(e.target.value)}
                />
                <button onClick={handleAddUser}>Add User</button>
            </div>

            <div className="assign-user">
                <h3>Assign User to Group</h3>
                <select
                    value={selectedUserId}
                    onChange={(e) => setSelectedUserId(e.target.value)}
                >
                    <option value="">Select User</option>
                    {allUsers.map((user) => (
                        <option key={user.unique_user} value={user.id}>
                            {user.name}
                        </option>
                    ))}
                </select>
                <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                >
                    <option value="member">Project Manager</option>
                    <option value="admin">Admin</option>
                    <option value="editor">Business Analyst</option>
                    <option value="viewer">Technical Leader</option>
                    <option value="owner">Summer Trainee</option>
                    <option value="guest">HR</option>
                </select>
                <button onClick={handleAssignUserToGroup}>Assign to Group</button>
            </div>
        </div>
    );
}

// Define PropTypes for the component
UsersPanel.propTypes = {
    groupId: PropTypes.string.isRequired, // Validate groupId as a required string
};

export default UsersPanel;
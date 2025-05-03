// This file is responsible for managing the users in a group.
// it includes functionality to create new users, assign them to a group, and 
// remove them from a group.

import React, { useEffect, useState } from "react";
import API from "../api";

function UsersPanel({ groupId }) {
    // values for the users panel
    const [users, setUsers] = useState([]);
    const [allUsers, setAllUsers] = useState([]);
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
        // this function handles the creation of a new user.
        // It checks if the user name, email, and password are provided.
        // If not, it alerts the user.
        // If the user name, email, and password are valid, it sends a POST request to create a new user.
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
                console.log("New user created:", response.data);
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
        // this function handles the assignment of a user to a group.
        // It checks if a user is selected. If not, it alerts the user.
        // If a user is selected, it sends a POST request to assign the user to the group.
        // If the user is already a member of the group, it alerts the user.
        if (!selectedUserId) {
            alert("Please select a user to assign to the group.");
            return;
        }

        const payload = { user_id: selectedUserId, role: selectedRole }; // Include the selected role

        API.post(`/groups/${groupId}/user/`, payload)
            .then((response) => {
                console.log("User assigned to group:", response.data);
                setUsers((prevUsers) => [...prevUsers, response.data]);
                setSelectedUserId("");
                setSelectedRole("member"); // Reset role to default
            })
            .catch((error) => {
                console.error("Error assigning user to group:", error.response?.data || error.message);
                alert(error.response?.data?.error || "Failed to assign user to group. Please try again.");
            });
    };

    const handleRemoveUserFromGroup = (userId) => {
        // this function handles the removal of a user from a group.
        // It prompts the user for confirmation before sending a DELETE request
        //  to remove the user. 
        console.log(`Removing user ${userId} from group ${groupId}`);
        API.delete(`/groups/${groupId}/user/`, {
            data: { user_id: userId }, // Send user_id in the request body
        })
            .then(() => {
                setUsers(users.filter((user) => user.id !== userId));
            })
            .catch((error) => console.error("Error deleting user:", error));
    };

    return (
        <div className="users-panel">
            <h2>Users in Group</h2>
            <ul className="user-list">
                {users.map((user) => (
                    <li key={user.id} className="user-item">
                        <div className="user-frame">
                            <div className="user-details">
                                <strong>Name:</strong> {user.name} <br />
                                <strong>Email:</strong> {user.email} <br />
                                <strong>Role:</strong> {user.role}
                            </div>
                            <div className="user-actions">
                                <button
                                    className="remove-button"
                                    onClick={() => handleRemoveUserFromGroup(user.id)}
                                >
                                    Remove
                                </button>
                            </div>
                        </div>
                    </li>
                ))}
            </ul>

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

export default UsersPanel;
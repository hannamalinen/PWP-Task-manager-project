import React, { useEffect, useState } from "react";
import API from "../api";

function UsersPanel({ groupId }) {
    const [users, setUsers] = useState([]); // List of users in the group
    const [allUsers, setAllUsers] = useState([]); // List of all users
    const [newUserName, setNewUserName] = useState(""); // State for the new user name
    const [newUserEmail, setNewUserEmail] = useState(""); // State for the new user email
    const [newUserPassword, setNewUserPassword] = useState(""); // State for the new user password
    const [selectedUserId, setSelectedUserId] = useState(""); // State for assigning a user to the group

    useEffect(() => {
        if (groupId) {
            // Fetch users in the group
            API.get(`/groups/${groupId}/members/`)
                .then((response) => {
                    console.log("Users in group fetched:", response.data);
                    setUsers(response.data);
                })
                .catch((error) => console.error("Error fetching users in group:", error));
        }

        // Fetch all users
        API.get("/users/")
            .then((response) => {
                console.log("All users fetched:", response.data);
                setAllUsers(response.data);
            })
            .catch((error) => console.error("Error fetching all users:", error));
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
                console.log("New user created:", response.data);
                setAllUsers((prevUsers) => [...prevUsers, response.data]); // Add the new user to the list
                setNewUserName(""); // Clear the name input field
                setNewUserEmail(""); // Clear the email input field
                setNewUserPassword(""); // Clear the password input field
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

        const role = "member"; // Default role for the user
        const payload = { user_id: selectedUserId, role };

        API.post(`/groups/${groupId}/user/`, payload)
            .then((response) => {
                console.log("User assigned to group:", response.data);
                setUsers((prevUsers) => [...prevUsers, response.data]); // Add the user to the group
                setSelectedUserId(""); // Clear the selection
            })
            .catch((error) => {
                console.error("Error assigning user to group:", error.response?.data || error.message);
                alert(error.response?.data?.error || "Failed to assign user to group. Please try again.");
            });
    };

    const handleRemoveUserFromGroup = (userId) => {
        API.delete(`/groups/${groupId}/user/`, {
            headers: { "Content-Type": "application/json" }, // Ensure the content type is JSON
            data: { user_id: userId }, // Pass the user ID in the request body
        })
            .then(() => {
                console.log(`User with ID ${userId} removed from group.`);
                setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId)); // Update the UI
            })
            .catch((error) => console.error("Error removing user from group:", error));
    };

    return (
        <div className="users-panel">
            <h2>Users</h2>

            {/* Add New User */}
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

            {/* Assign User to Group */}
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
                <button onClick={handleAssignUserToGroup}>Assign to Group</button>
            </div>

            {/* List Users in Group */}
            <h3>Users in Group</h3>
            <ul>
                {users.map((user) => (
                    <li key={user.id}>
                        {user.name}
                        <button onClick={() => handleRemoveUserFromGroup(user.id)}>Remove</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default UsersPanel;
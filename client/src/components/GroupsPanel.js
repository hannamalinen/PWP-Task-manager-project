// This file handles the group management functionality.
// it allows users to create, edit, and delete groups.
// It also allows users to select a group to view its tasks and users.
import React, { useEffect, useState } from "react";
import API from "../api";

function GroupsPanel({ onGroupSelect }) {
    // This component manages the groups in the application. 
    const [groups, setGroups] = useState([]);
    const [users, setUsers] = useState([]); // Track users in the selected group
    const [selectedGroupId, setSelectedGroupId] = useState(null);
    const [selectedGroupName, setSelectedGroupName] = useState("");
    const [newGroupName, setNewGroupName] = useState("");
    const [editingGroupId, setEditingGroupId] = useState(null);
    const [editingGroupName, setEditingGroupName] = useState("");

    useEffect(() => {
        API.get("/groups/")
            .then((response) => setGroups(response.data))
            .catch((error) => console.error("Error fetching groups:", error));
    }, []);

    useEffect(() => {
        if (selectedGroupId) {
            API.get(`/groups/${selectedGroupId}/users/`)
                .then((response) => {
                    setUsers(response.data); // Ensure roles are included in the response
                })
                .catch((error) => console.error("Error fetching users in group:", error));
        }
    }, [selectedGroupId]);

    const handleCreateGroup = () => {
        // this function handles the creation of a new group.
        // It checks if the group name is provided. If not, it alerts the user.
        // If the group name is valid, it sends a POST request to create a new group.
        if (!newGroupName.trim()) {
            alert("Group name is required.");
            return;
        }

        API.post("/groups/", { name: newGroupName })
            .then((response) => {
                setGroups((prevGroups) => [...prevGroups, response.data]);
                setNewGroupName("");
            })
            .catch((error) => console.error("Error creating group:", error));
    };

    const handleDeleteGroup = (groupId) => {
        // this function handles the deletion of a group.
        // It prompts the user for confirmation before sending a DELETE request to remove the group.
        // If the user confirms, it filters out the deleted group from the state.
        // If the user cancels, it does nothing.
        if (!window.confirm("Are you sure you want to delete this group?")) return;

        API.delete(`/groups/${groupId}/`)
            .then(() => {
                setGroups((prevGroups) => prevGroups.filter((group) => group.id !== groupId));
            })
            .catch((error) => console.error("Error deleting group:", error));
    };

    const handleEditGroup = (groupId, groupName) => {
        // this function handles the editing of a group.
        // It sets the editing group ID and name in the state.
        // This allows the user to edit the group's name.
        setEditingGroupId(groupId);
        setEditingGroupName(groupName);
    };

    const handleUpdateGroup = () => {
        if (!editingGroupName.trim()) {
            alert("Group name is required.");
            return;
        }

        API.put(`/groups/${editingGroupId}/`, { name: editingGroupName })
            .then((response) => {
                setGroups((prevGroups) =>
                    prevGroups.map((group) =>
                        group.id === editingGroupId ? response.data : group
                    )
                );
                setEditingGroupId(null);
                setEditingGroupName("");
            })
            .catch((error) => console.error("Error updating group:", error));
    };

    const handleGroupSelect = (groupId, groupName) => {
        setSelectedGroupId(groupId);
        setSelectedGroupName(groupName);
        onGroupSelect(groupId, groupName);
    };

    return (
        <div className="groups-panel">
            <h2>Groups</h2>
            <ul className="group-list">
                {groups.map((group) => (
                    <li key={group.id} className="group-item">
                        <div className="group-frame">
                            <span
                                className="group-name"
                                onClick={() => handleGroupSelect(group.id, group.name)}
                            >
                                {group.name}
                            </span>
                            <button
                                className="edit-button"
                                onClick={() => handleEditGroup(group.id, group.name)}
                            >
                                Edit
                            </button>
                            <button
                                className="delete-button"
                                onClick={() => handleDeleteGroup(group.id)}
                            >
                                Delete
                            </button>
                        </div>
                    </li>
                ))}
            </ul>

            {selectedGroupId && (
                <div className="users-in-group">
                    <h3>Users in {selectedGroupName}</h3>
                    <ul>
                        {users.map((user) => (
                            <li key={user.id}>
                                {user.name} - <strong>{user.role}</strong>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            <div className="create-group">
                <input
                    type="text"
                    placeholder="New Group Name"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                />
                <button onClick={handleCreateGroup}>Create Group</button>
            </div>
            {editingGroupId && (
                <div className="edit-group">
                    <input
                        type="text"
                        placeholder="Edit Group Name"
                        value={editingGroupName}
                        onChange={(e) => setEditingGroupName(e.target.value)}
                    />
                    <button onClick={handleUpdateGroup}>Update</button>
                    <button onClick={() => setEditingGroupId(null)}>Cancel</button>
                </div>
            )}
        </div>
    );
}

export default GroupsPanel;
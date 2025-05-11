/**
 * This file handles the group management functionality.
 * it allows users to create, edit, and delete groups.
 * It also allows users to select a group to view its tasks and users.
 */
import React, { useEffect, useState } from "react";
import PropTypes from "prop-types"; // Import PropTypes
import API from "../api";

/**
 * GroupsPanel component for managing groups in the application.
 */
function GroupsPanel({ onGroupSelect }) {
    const [groups, setGroups] = useState([]);
    const [users, setUsers] = useState([]); // Track users in the selected group
    const [selectedGroupId, setSelectedGroupId] = useState(null);
    const [selectedGroupName, setSelectedGroupName] = useState("");
    const [newGroupName, setNewGroupName] = useState("");
    const [editingGroupId, setEditingGroupId] = useState(null);
    const [editingGroupName, setEditingGroupName] = useState("");

    /**
     * Fetches the list of groups from the backend when the component mounts.
     */
    useEffect(() => {
        API.get("/groups/")
            .then((response) => setGroups(response.data))
            .catch((error) => console.error("Error fetching groups:", error));
    }, []);

    /**
     * Fetches the list of users in the selected group whenever the selected group changes.
     */
    useEffect(() => {
        if (selectedGroupId) {
            API.get(`/groups/${selectedGroupId}/users/`)
                .then((response) => {
                    setUsers(response.data); // Ensure roles are included in the response
                })
                .catch((error) => console.error("Error fetching users in group:", error));
        }
    }, [selectedGroupId]);

    /**
     * Handles the creation of a new group.
     * Validates the group name and sends a POST request to the backend.
     * Updates the group list and clears the input field on success.
     */
    const handleCreateGroup = () => {
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

    /**
     * Handles the deletion of a group.
     * Prompts the user for confirmation and sends a DELETE request to the backend.
     * Updates the group list on success.
     *
     * @param {number} groupId - The ID of the group to delete.
     */
    const handleDeleteGroup = (groupId) => {
        if (!window.confirm("Are you sure you want to delete this group?")) return;

        API.delete(`/groups/${groupId}/`)
            .then(() => {
                setGroups((prevGroups) => prevGroups.filter((group) => group.id !== groupId));
            })
            .catch((error) => console.error("Error deleting group:", error));
    };

    /**
     * Handles the initiation of group editing.
     * Sets the editing group ID and name in the state.
     *
     * @param {number} groupId - The ID of the group to edit.
     * @param {string} groupName - The current name of the group.
     */
    const handleEditGroup = (groupId, groupName) => {
        setEditingGroupId(groupId);
        setEditingGroupName(groupName);
    };

    /**
     * Handles the update of a group's name.
     * Validates the new name and sends a PUT request to the backend.
     * Updates the group list and clears the editing state on success.
     */
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

    /**
     * Handles the selection of a group.
     * Updates the selected group ID and name in the state and notifies the parent component.
     *
     * @param {number} groupId - The ID of the selected group.
     * @param {string} groupName - The name of the selected group.
     */
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

// Define PropTypes for the component
GroupsPanel.propTypes = {
    onGroupSelect: PropTypes.func.isRequired, // Ensure onGroupSelect is a required function
};

export default GroupsPanel;
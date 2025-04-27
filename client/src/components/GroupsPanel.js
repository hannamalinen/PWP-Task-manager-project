import React, { useEffect, useState } from "react";
import API from "../api";

function GroupsPanel({ onGroupSelect }) {
    const [groups, setGroups] = useState([]);
    const [newGroupName, setNewGroupName] = useState("");
    const [editingGroupId, setEditingGroupId] = useState(null);
    const [editingGroupName, setEditingGroupName] = useState("");

    useEffect(() => {
        API.get("/groups/")
            .then((response) => setGroups(response.data))
            .catch((error) => console.error("Error fetching groups:", error));
    }, []);

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

    const handleDeleteGroup = (groupId) => {
        if (!window.confirm("Are you sure you want to delete this group?")) return;

        API.delete(`/groups/${groupId}/`)
            .then(() => {
                setGroups((prevGroups) => prevGroups.filter((group) => group.id !== groupId));
            })
            .catch((error) => console.error("Error deleting group:", error));
    };

    const handleEditGroup = (groupId, groupName) => {
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

    return (
        <div className="groups-panel">
            <h2>Groups</h2>
            <ul className="group-list">
                {groups.map((group) => (
                    <li key={group.id} className="group-item">
                        <div className="group-frame">
                            <span
                                className="group-name"
                                onClick={() => onGroupSelect(group.id, group.name)}
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
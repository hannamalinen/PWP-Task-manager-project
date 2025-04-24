import React, { useEffect, useState } from "react";
import API from "../api";

function GroupsPanel({ onGroupSelect }) {
    const [groups, setGroups] = useState([]);
    const [newGroupName, setNewGroupName] = useState(""); // State for the new group name
    const [editingGroupId, setEditingGroupId] = useState(null); // State for the group being edited
    const [updatedGroupName, setUpdatedGroupName] = useState(""); // State for the updated group name

    useEffect(() => {
        API.get("/groups/")
            .then((response) => {
                console.log("Groups fetched from API:", response.data); // Log the API response
                setGroups(response.data); // Use response.data if the API returns a flat array
            })
            .catch((error) => console.error("Error fetching groups:", error));
    }, []);

    const handleAddGroup = () => {
        if (!newGroupName.trim()) {
            alert("Group name is required.");
            return;
        }

        API.post("/groups/", { name: newGroupName })
            .then((response) => {
                console.log("New group created:", response.data);
                setGroups((prevGroups) => [...prevGroups, response.data]); // Add the new group to the list
                setNewGroupName(""); // Clear the input field
            })
            .catch((error) => console.error("Error creating group:", error));
    };

    const handleDeleteGroup = (groupId) => {
        API.delete(`/groups/${groupId}/`)
            .then(() => {
                console.log(`Group with ID ${groupId} deleted.`);
                setGroups((prevGroups) => prevGroups.filter((group) => group.id !== groupId)); // Remove the group from the list
            })
            .catch((error) => console.error("Error deleting group:", error));
    };

    const handleUpdateGroup = (groupId) => {
        if (!updatedGroupName.trim()) {
            alert("Updated group name is required.");
            return;
        }

        API.put(`/groups/${groupId}/`, { name: updatedGroupName })
            .then((response) => {
                console.log("Group updated:", response.data);
                setGroups((prevGroups) =>
                    prevGroups.map((group) =>
                        group.id === groupId ? { ...group, name: response.data.name } : group
                    )
                );
                setEditingGroupId(null); // Exit edit mode
                setUpdatedGroupName(""); // Clear the input field
            })
            .catch((error) => console.error("Error updating group:", error));
    };

    return (
        <div className="groups-panel">
            <h2>Groups</h2>
            <ul>
                {groups.map((group) => (
                    <li key={group.unique_group}>
                        {editingGroupId === group.id ? (
                            <>
                                <input
                                    type="text"
                                    value={updatedGroupName}
                                    onChange={(e) => setUpdatedGroupName(e.target.value)}
                                    placeholder="Update Group Name"
                                />
                                <button onClick={() => handleUpdateGroup(group.id)}>Save</button>
                                <button onClick={() => setEditingGroupId(null)}>Cancel</button>
                            </>
                        ) : (
                            <>
                                <span onClick={() => onGroupSelect(group.id)}>{group.name}</span>
                                <button onClick={() => setEditingGroupId(group.id)}>Edit</button>
                                <button onClick={() => handleDeleteGroup(group.id)}>Delete</button>
                            </>
                        )}
                    </li>
                ))}
            </ul>
            <div className="add-group">
                <input
                    type="text"
                    placeholder="New Group Name"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                />
                <button onClick={handleAddGroup}>Add Group</button>
            </div>
        </div>
    );
}

export default GroupsPanel;
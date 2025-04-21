import React, { useEffect, useState } from "react";
import API from "../api";

function GroupsPanel({ onGroupSelect }) {
    const [groups, setGroups] = useState([]);

    useEffect(() => {
        API.get("/groups/")
            .then((response) => {
                console.log("Groups fetched from API:", response.data); // Log the API response
                setGroups(response.data); // Use response.data if the API returns a flat array
            })
            .catch((error) => console.error("Error fetching groups:", error));
    }, []);

    console.log("Groups state:", groups); // Log the current state of groups

    return (
        <div className="groups-panel">
            <h2>Groups</h2>
            <ul>
                {groups.map((group) => (
                    <li key={group.id} onClick={() => onGroupSelect(group.id)}>
                        {group.name}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default GroupsPanel;
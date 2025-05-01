import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api";

function MainPage() {
    const [groups, setGroups] = useState([]);

    useEffect(() => {
        API.get("/groups/")
            .then((response) => setGroups(response.data))
            .catch((error) => console.error("Error fetching groups:", error));
    }, []);

    return (
        <div className="main-page">
            <h2>All Groups</h2>
            <div className="group-list">
                {groups.map((group) => (
                    <Link to={`/group/${group.id}`} key={group.id} className="group-card">
                        {group.name}
                    </Link>
                ))}
            </div>
        </div>
    );
}

export default MainPage;
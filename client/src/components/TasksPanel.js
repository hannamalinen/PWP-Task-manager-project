import React, { useEffect, useState } from "react";
import API from "../api";

function TasksPanel({ groupId }) {
    const [tasks, setTasks] = useState([]);

    useEffect(() => {
        if (groupId) {
            API.get(`/groups/${groupId}/tasks/`)
                .then((response) => setTasks(response.data.items))
                .catch((error) => console.error("Error fetching tasks:", error));
        }
    }, [groupId]);

    return (
        <div className="tasks-panel">
            <h2>Tasks</h2>
            <ul>
                {tasks.map((task) => (
                    <li key={task.id}>
                        {task.title} - {task.status === 1 ? "Completed" : "Pending"}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default TasksPanel;
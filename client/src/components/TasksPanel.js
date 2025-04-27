import React, { useEffect, useState } from "react";
import API from "../api";

function TasksPanel({ groupId, onEditTask }) {
    const [tasks, setTasks] = useState([]);

    useEffect(() => {
        if (groupId) {
            API.get(`/groups/${groupId}/tasks/`)
                .then((response) => setTasks(response.data || []))
                .catch((error) => console.error("Error fetching tasks:", error));
        }
    }, [groupId]);

    const handleDelete = (uniqueTask) => {
        if (!window.confirm("Are you sure you want to delete this task?")) return;

        API.delete(`/groups/${groupId}/tasks/${uniqueTask}/`)
            .then(() => {
                setTasks((prevTasks) => prevTasks.filter((task) => task.unique_task !== uniqueTask));
            })
            .catch((error) => console.error("Error deleting task:", error));
    };

    return (
        <div className="tasks-panel">
            <h2>Tasks</h2>
            <ul className="task-list">
                {tasks.map((task) => (
                    <li key={task.id} className="task-item">
                        <div className="task-frame">
                            <div className="task-details">
                                <strong>Title:</strong> {task.title} <br />
                                <strong>Description:</strong> {task.description} <br />
                                <strong>Status:</strong> {task.status === 1 ? "Completed" : "Pending"} <br />
                                <strong>Deadline:</strong> {new Date(task.deadline).toLocaleString()} <br />
                            </div>
                            <div className="task-actions">
                                <button className="edit-button" onClick={() => onEditTask(task)}>
                                    Edit
                                </button>
                                <button className="delete-button" onClick={() => handleDelete(task.unique_task)}>
                                    Delete
                                </button>
                            </div>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default TasksPanel;
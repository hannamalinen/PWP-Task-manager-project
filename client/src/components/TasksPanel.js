import React from "react";
import API from "../api";

function TasksPanel({ groupId, tasks, onEditTask }) {
    const handleDelete = (uniqueTask) => {
        if (!window.confirm("Are you sure you want to delete this task?")) return;

        API.delete(`/groups/${groupId}/tasks/${uniqueTask}/`)
            .then(() => {
                // Notify parent to update tasks
                const updatedTasks = tasks.filter((task) => task.unique_task !== uniqueTask);
                onEditTask(updatedTasks); // Optional: Notify parent if needed
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
                                <strong>Title:</strong> <strong>{task.title}</strong> <br />
                                <strong>Description:</strong> {task.description} <br />
                                <strong>Status:</strong> {task.status === 1 ? "Completed" : "Pending"} <br />
                                <strong>Deadline:</strong> {new Date(task.deadline).toLocaleString()} <br />
                                <strong>Created At:</strong> {new Date(task.created_at).toLocaleString()} <br />
                                <strong>Last Modified:</strong> {new Date(task.updated_at).toLocaleString()} <br />
                            </div>
                            <div className="task-actions">
                                <button
                                    className="edit-button"
                                    onClick={() => onEditTask(task)} // Call the edit handler
                                >
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
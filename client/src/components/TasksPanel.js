import React, { useEffect, useState } from "react";
import API from "../api";

function TasksPanel({ groupId, onEditTask }) {
    const [tasks, setTasks] = useState([]); // Initialize as an empty array

    useEffect(() => {
        if (groupId) {
            API.get(`/groups/${groupId}/tasks/`)
                .then((response) => {
                    console.log("Tasks fetched:", response.data); // Debugging
                    setTasks(response.data || []); // Ensure tasks is an array
                })
                .catch((error) => console.error("Error fetching tasks:", error));
        }
    }, [groupId]);

    const handleDelete = (uniqueTask) => {
        console.log("Deleting task with unique_task:", uniqueTask, "from group:", groupId); // Debugging

        API.delete(`/groups/${groupId}/tasks/${uniqueTask}/`)
            .then(() => {
                setTasks((prevTasks) => prevTasks.filter((task) => task.unique_task !== uniqueTask));
                console.log("Task deleted successfully");
            })
            .catch((error) => {
                console.error("Error deleting task:", error.response?.data || error.message);
            });
    };

    const handleEdit = (task) => {
        console.log("Editing task:", task); // Debugging
        onEditTask(task); // Pass the task to the parent component for editing
    };

    return (
        <div className="tasks-panel">
            <h2>Tasks</h2>
            <ul>
                {tasks.length > 0 ? (
                    tasks.map((task) => (
                        <li key={task.id}>
                            <strong>Title:</strong> {task.title} <br />
                            <strong>Description:</strong> {task.description} <br />
                            <strong>Status:</strong> {task.status === 1 ? "Completed" : "Pending"} <br />
                            <strong>Deadline:</strong> {new Date(task.deadline).toLocaleString()} <br />
                            <strong>Created At:</strong> {new Date(task.created_at).toLocaleString()} <br />
                            <strong>Updated At:</strong> {new Date(task.updated_at).toLocaleString()} <br />
                            <button onClick={() => handleEdit(task)}>Edit</button>
                            <button onClick={() => handleDelete(task.unique_task)}>Delete</button>
                        </li>
                    ))
                ) : (
                    <p>No tasks available</p>
                )}
            </ul>
        </div>
    );
}

export default TasksPanel;
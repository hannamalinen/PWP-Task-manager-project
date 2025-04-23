import React, { useState, useEffect } from "react";
import API from "../api";

function TaskForm({ groupId, onTaskCreated, taskToEdit, onTaskUpdated }) {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [status, setStatus] = useState(0); // Default to "Pending"
    const [deadline, setDeadline] = useState("");

    // Populate the form if editing an existing task
    useEffect(() => {
        if (taskToEdit) {
            setTitle(taskToEdit.title);
            setDescription(taskToEdit.description);
            setStatus(taskToEdit.status);
            setDeadline(taskToEdit.deadline);
        }
    }, [taskToEdit]);

    const handleSubmit = (e) => {
        e.preventDefault();

        const taskData = {
            title,
            description,
            status,
            deadline,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };

        if (taskToEdit) {
            // Update an existing task
            API.put(`/groups/${groupId}/tasks/${taskToEdit.unique_task}/`, taskData)
                .then((response) => {
                    onTaskUpdated(response.data);
                    setTitle("");
                    setDescription("");
                    setStatus(0);
                    setDeadline("");
                })
                .catch((error) => console.error("Error updating task:", error));
        } else {
            // Create a new task
            API.post(`/groups/${groupId}/tasks/`, taskData)
                .then((response) => {
                    onTaskCreated(response.data);
                    setTitle("");
                    setDescription("");
                    setStatus(0);
                    setDeadline("");
                    
                })
                .catch((error) => console.error("Error creating task:", error));
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Task Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
            />
            <textarea
                placeholder="Task Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
            />
            <select value={status} onChange={(e) => setStatus(Number(e.target.value))}>
                <option value={0}>Pending</option>
                <option value={1}>Completed</option>
            </select>
            <input
                type="datetime-local"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
            />
            <button type="submit">{taskToEdit ? "Update Task" : "Create Task"}</button>
        </form>
    );
}

export default TaskForm;

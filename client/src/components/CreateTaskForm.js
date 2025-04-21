import React, { useState, useEffect } from "react";
import API from "../api";

function TaskForm({ groupId, onTaskCreated, taskToEdit, onTaskUpdated }) {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");

    // Populate the form if editing an existing task
    useEffect(() => {
        if (taskToEdit) {
            setTitle(taskToEdit.title);
            setDescription(taskToEdit.description);
        }
    }, [taskToEdit]);

    const handleSubmit = (e) => {
        e.preventDefault();

        if (taskToEdit) {
            // Update an existing task
            API.put(`/groups/${groupId}/tasks/${taskToEdit.id}/`, { title, description })
                .then((response) => {
                    onTaskUpdated(response.data);
                    setTitle("");
                    setDescription("");
                })
                .catch((error) => console.error("Error updating task:", error));
        } else {
            // Create a new task
            API.post(`/groups/${groupId}/tasks/`, { title, description })
                .then((response) => {
                    onTaskCreated(response.data);
                    setTitle("");
                    setDescription("");
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
            <button type="submit">{taskToEdit ? "Update Task" : "Create Task"}</button>
        </form>
    );
}

export default TaskForm;
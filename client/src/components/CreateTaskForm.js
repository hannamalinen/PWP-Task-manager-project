import React, { useState, useEffect } from "react";
import API from "../api";

function TaskForm({ groupId, onTaskCreated, taskToEdit, onTaskUpdated, onCancelEdit }) {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [status, setStatus] = useState(0); // Default to "Pending"
    const [deadline, setDeadline] = useState("");

    useEffect(() => {
        if (taskToEdit) {
            console.log("Editing task:", taskToEdit); // Debugging
            setTitle(taskToEdit.title || "");
            setDescription(taskToEdit.description || "");
            setStatus(taskToEdit.status || 0);
            setDeadline(taskToEdit.deadline || "");
        } else {
            // Reset the form when no task is being edited
            setTitle("");
            setDescription("");
            setStatus(0);
            setDeadline("");
        }
    }, [taskToEdit]);

    const getLocalISOString = () => {
        const now = new Date();
        const offset = now.getTimezoneOffset() * 60000; // Offset in milliseconds
        const localTime = new Date(now.getTime() - offset);
        return localTime.toISOString().slice(0, 19); // Remove milliseconds and 'Z'
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        // Validation: Check each field and show specific alerts
        if (!title.trim()) {
            alert("Task title is required.");
            return;
        }
        if (!description.trim()) {
            alert("Task description is required.");
            return;
        }
        if (!deadline) {
            alert("Task deadline is required.");
            return;
        }

        // Validation: Ensure deadline is not in the past
        const currentDate = new Date();
        const selectedDate = new Date(deadline);

        if (selectedDate < currentDate) {
            alert("Task deadline cannot be earlier than the current date.");
            return;
        }

        const taskData = {
            title: title.trim(),
            description: description.trim(),
            status,
            deadline,
            created_at: getLocalISOString(), // Use local time
            updated_at: getLocalISOString(), // Use local time
        };

        if (taskToEdit) {
            // Update an existing task
            API.put(`/groups/${groupId}/tasks/${taskToEdit}/`, taskData)
                .then((response) => {
                    onTaskUpdated(response.data);
                })
                .catch((error) => console.error("Error updating task:", error));
        } else {
            // Create a new task
            API.post(`/groups/${groupId}/tasks/`, taskData)
                .then((response) => {
                    onTaskCreated(response.data);
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
                min={new Date().toISOString().slice(0, 16)} // Prevent selecting past dates
            />
            <button type="submit">{taskToEdit ? "Update Task" : "Create Task"}</button>
            {taskToEdit && (
                <button type="button" onClick={onCancelEdit}>
                    Cancel Edit
                </button>
            )}
        </form>
    );
}

export default TaskForm;

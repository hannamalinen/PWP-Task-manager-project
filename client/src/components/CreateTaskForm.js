// This file creates a form for creating and editing tasks.
// It includes fields for task title, description, status, and deadline.
// It also includes validation for required fields and handles the submission of the form.
import React, { useState, useEffect } from "react";
import API from "../api";

function CreateTaskForm({ groupId, taskToEdit, onTaskCreated, onTaskUpdated, onCancelEdit }) {
    // This component is responsible for creating and editing tasks.
    const [title, setTitle] = useState(taskToEdit ? taskToEdit.title : "");
    const [description, setDescription] = useState(taskToEdit ? taskToEdit.description : "");
    const [status, setStatus] = useState(0); // Default to "Pending"
    const [deadline, setDeadline] = useState("");

    useEffect(() => {
        if (taskToEdit) {
            // If editing a task, set the form fields to the task's current values
            setTitle(taskToEdit.title || "");
            setDescription(taskToEdit.description || "");
            setStatus(taskToEdit.status || 0);
            setDeadline(taskToEdit.deadline || "");
        } else {
            setTitle("");
            setDescription("");
            setStatus(0);
            setDeadline("");
        }
    }, [taskToEdit]);

    const getLocalISOString = () => {
        // This function gets the current local date and time in ISO format.
        const now = new Date();
        const offset = now.getTimezoneOffset() * 60000; // Offset in milliseconds
        const localTime = new Date(now.getTime() - offset);
        return localTime.toISOString().slice(0, 19); // Remove milliseconds and 'Z'
    };

    const handleSubmit = (e) => {
        e.preventDefault();

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

        const taskData = {
            title: title.trim(),
            description: description.trim(),
            status, // Include the status field
            deadline: new Date(deadline).toISOString(), // Convert to full ISO 8601 format
            created_at: taskToEdit ? taskToEdit.created_at : new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };

        console.log("Payload being sent to the backend:", taskData); // Log the payload

        if (taskToEdit) {
            API.put(`/groups/${groupId}/tasks/${taskToEdit.unique_task}/`, taskData)
                .then((response) => {
                    onTaskUpdated(response.data);
                })
                .catch((error) => console.error("Error updating task:", error.response?.data || error.message));
        } else {
            API.post(`/groups/${groupId}/tasks/`, taskData)
                .then((response) => {
                    onTaskCreated(response.data);
                })
                .catch((error) => {
                    console.error("Error creating task:", error.response?.data || error.message);
                });
        }
    };

    return (
        <div className="create-task-form">
            {/* Dynamically change the header based on the mode */}
            <h3>{taskToEdit ? "Edit Task" : "Create Task"}</h3>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Task Title</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Enter task title"
                    />
                </div>
                <div className="form-group">
                    <label>Task Description</label>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Enter task description"
                    />
                </div>
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
                {taskToEdit && <button onClick={onCancelEdit}>Cancel</button>}
            </form>
        </div>
    );
}

export default CreateTaskForm;

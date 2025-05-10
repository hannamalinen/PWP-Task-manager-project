// This file creates a form for creating and editing tasks.
// It includes fields for task title, description, status, and deadline.
// It also includes validation for required fields and handles the submission of the form.
import React, { useState, useEffect } from "react";
import PropTypes from "prop-types"; // Import PropTypes
import API from "../api";

function CreateTaskForm({ groupId, taskToEdit, onTaskCreated, onCancelEdit }) {
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

    const getLocalISOString = (date) => {
        // This function gets the local date and time in ISO format without the 'Z' suffix.
        const now = date ? new Date(date) : new Date();
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

        // Format the deadline and timestamps using getLocalISOString
        const formattedDeadline = getLocalISOString(deadline);
        const formattedCreatedAt = getLocalISOString(); // Current time
        const formattedUpdatedAt = getLocalISOString(); // Current time

        const payload = {
            title,
            description,
            status,
            deadline: formattedDeadline,
            created_at: formattedCreatedAt,
            updated_at: formattedUpdatedAt,
        };

        API.post(`/groups/${groupId}/tasks/`, payload)
            .then((response) => {
                console.log("Task created successfully:", response.data);
                onTaskCreated(response.data); // Update the task list
            })
            .catch((error) => {
                console.error("Error creating task:", error.response?.data || error.message);
                alert(error.response?.data?.message || "Failed to create task. Please try again.");
            });
    };

    return (
        <div className="create-task-form">
            {/* Dynamically change the header based on the mode */}
            <h3>{taskToEdit ? "Edit Task" : "Create A Task"}</h3>
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

// Define PropTypes for the component
CreateTaskForm.propTypes = {
    groupId: PropTypes.string.isRequired, // groupId must be a string and is required
    taskToEdit: PropTypes.shape({
        title: PropTypes.string,
        description: PropTypes.string,
        status: PropTypes.number,
        deadline: PropTypes.string,
    }), // taskToEdit is an object with optional fields
    onTaskCreated: PropTypes.func.isRequired, // onTaskCreated must be a function and is required
    onCancelEdit: PropTypes.func.isRequired, // onCancelEdit must be a function and is required
};

export default CreateTaskForm;

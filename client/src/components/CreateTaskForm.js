import React, { useState, useEffect } from "react";
import API from "../api";

function CreateTaskForm({ groupId, taskToEdit, onTaskCreated, onTaskUpdated, onCancelEdit }) {
    const [title, setTitle] = useState(taskToEdit ? taskToEdit.title : "");
    const [description, setDescription] = useState(taskToEdit ? taskToEdit.description : "");
    const [status, setStatus] = useState(0); // Default to "Pending"
    const [deadline, setDeadline] = useState("");

    useEffect(() => {
        if (taskToEdit) {
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
            deadline,
            created_at: taskToEdit ? taskToEdit.created_at : new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };

        if (taskToEdit) {
            // Update existing task
            API.put(`/groups/${groupId}/tasks/${taskToEdit.unique_task}/`, taskData)
                .then((response) => {
                    onTaskUpdated(response.data); // Notify parent of the updated task
                })
                .catch((error) => console.error("Error updating task:", error));
        } else {
            // Create new task
            API.post(`/groups/${groupId}/tasks/`, taskData)
                .then((response) => {
                    onTaskCreated(response.data); // Notify parent of the new task
                })
                .catch((error) => console.error("Error creating task:", error));
        }
    };

    return (
        <div className="create-task-form">
            <h3>Create/Edit Task</h3> {/* Add title */}
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

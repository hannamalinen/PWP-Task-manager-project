/** 
 * This file manages the tasks in a group.
 * It allows users to view, edit, and delete tasks.
 */

import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import "./TasksPanel.css"; // Import CSS for styling
import API from "../api";

/**
 * TasksPanel component for managing tasks in a group.
 */
function TasksPanel({ groupId }) {
    const [tasks, setTasks] = useState([]);
    const [completedCount, setCompletedCount] = useState(0);
    const [pendingCount, setPendingCount] = useState(0);
    const [selectedTask, setSelectedTask] = useState(null); // Track the selected task for details
    const [isEditing, setIsEditing] = useState(false); // Track if the task is being edited

    useEffect(() => {
        if (groupId) {
            API.get(`/groups/${groupId}/tasks/`)
                .then((response) => {
                    const tasks = response.data || [];
                    tasks.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
                    setTasks(tasks);

                    const completed = tasks.filter((task) => task.status === 1).length;
                    const pending = tasks.filter((task) => task.status === 0).length;

                    setCompletedCount(completed);
                    setPendingCount(pending);
                })
                .catch((error) => console.error("Error fetching tasks:", error));
        }
    }, [groupId]);

    /**
     * Handles the selection of a task for viewing or editing.
     *
     * @param {Object} task - The task to be selected.
     */
    const handleTaskClick = (task) => {
        setSelectedTask(task); // Set the clicked task as the selected task
        setIsEditing(false); // Ensure editing mode is off when opening the modal
    };

    /**
     * Closes the task details modal.
     */
    const handleCloseDetails = () => {
        setSelectedTask(null); // Clear the selected task
    };

    /**
     * Toggles the status of a task between pending and completed.
     *
     * @param {Object} task - The task whose status is being toggled.
     */
    const handleToggleStatus = (task) => {
        const updatedTask = { ...task, status: task.status === 1 ? 0 : 1 }; // Toggle status
        API.put(`/groups/${groupId}/tasks/${task.unique_task}/`, updatedTask)
            .then((response) => {
                setTasks((prevTasks) =>
                    prevTasks.map((t) =>
                        t.unique_task === task.unique_task ? response.data : t
                    )
                );
                setCompletedCount((prev) =>
                    task.status === 0 ? prev + 1 : prev - 1
                );
                setPendingCount((prev) =>
                    task.status === 0 ? prev - 1 : prev + 1
                );
            })
            .catch((error) => console.error("Error toggling task status:", error));
    };

    /**
     * Saves the changes made to a task.
     */
    const handleSaveTask = () => {
        API.put(`/groups/${groupId}/tasks/${selectedTask.unique_task}/`, selectedTask)
            .then((response) => {
                setTasks((prevTasks) =>
                    prevTasks.map((task) =>
                        task.unique_task === selectedTask.unique_task
                            ? response.data
                            : task
                    )
                );
                setSelectedTask(null); // Close the modal after saving
            })
            .catch((error) => console.error("Error saving task:", error));
    };

    /**
     * Deletes a task from the group.
     *
     * @param {number} taskId - The ID of the task to delete.
     */
    const handleDelete = (taskId) => {
        API.delete(`/groups/${groupId}/tasks/${taskId}/`)
            .then(() => {
                setTasks((prevTasks) =>
                    prevTasks.filter((task) => task.unique_task !== taskId)
                );
                setSelectedTask(null); // Close the modal after deletion
            })
            .catch((error) => console.error("Error deleting task:", error));
    };

    const totalTasks = completedCount + pendingCount;

    const completedTasks = tasks.filter((task) => task.status === 1);
    const pendingTasks = tasks.filter((task) => task.status === 0);

    return (
        <div className="tasks-panel">
            <h2>Tasks</h2>

            {/* Task Summary Section */}
            <div className="task-summary">
                <div className="circular-progress-container">
                    <div className="circular-progress">
                        <CircularProgressbar
                            value={totalTasks > 0 ? (pendingCount / totalTasks) * 100 : 0}
                            styles={buildStyles({
                                textColor: "#f44336",
                                pathColor: "#f44336",
                                trailColor: "#e0e0e0",
                            })}
                        />
                        <p className="progress-text">Pending: {pendingCount}</p>
                    </div>
                    <div className="circular-progress">
                        <CircularProgressbar
                            value={totalTasks > 0 ? (completedCount / totalTasks) * 100 : 0}
                            styles={buildStyles({
                                textColor: "#4caf50",
                                pathColor: "#4caf50",
                                trailColor: "#e0e0e0",
                            })}
                        />
                        <p className="progress-text">Completed: {completedCount}</p>
                    </div>
                </div>
            </div>

            <div className="tasks-container">
                {/* Pending Tasks Section */}
                <div className="task-section pending-tasks">
                    <h3>Pending Tasks</h3>
                    <div className="task-list">
                        {pendingTasks.map((task) => (
                            <div key={task.unique_task} className="task-card pink-card">
                                <div className="task-header">
                                    <h3>{task.title}</h3>
                                    <p><strong>Deadline:</strong> {new Date(task.deadline).toLocaleString()}</p>
                                </div>
                                <div className="task-actions">
                                    <button
                                        className="mark-completed"
                                        onClick={() => handleToggleStatus(task)}
                                    >
                                        ✅ Mark as Completed
                                    </button>
                                    <button
                                        className="view-details"
                                        onClick={() => handleTaskClick(task)}
                                    >
                                        🔍 View Details
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Completed Tasks Section */}
                <div className="task-section completed-tasks">
                    <h3>Completed Tasks</h3>
                    <div className="task-list">
                        {completedTasks.map((task) => (
                            <div key={task.unique_task} className="task-card green-card">
                                <div className="task-header">
                                    <h3>{task.title}</h3>
                                    <p><strong>Completed At:</strong> {new Date(task.updated_at).toLocaleString()}</p>
                                </div>
                                <div className="task-actions">
                                    <button
                                        className="view-details"
                                        onClick={() => handleTaskClick(task)}
                                    >
                                        🔍 View Details
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Task Details Modal */}
            {selectedTask && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>Task Details</h3>
                        {isEditing ? (
                            <form
                                onSubmit={(e) => {
                                    e.preventDefault();
                                    handleSaveTask();
                                }}
                            >
                                <label>
                                    Title:
                                    <input
                                        type="text"
                                        value={selectedTask.title}
                                        onChange={(e) =>
                                            setSelectedTask({
                                                ...selectedTask,
                                                title: e.target.value,
                                            })
                                        }
                                    />
                                </label>
                                <label>
                                    Description:
                                    <textarea
                                        value={selectedTask.description}
                                        onChange={(e) =>
                                            setSelectedTask({
                                                ...selectedTask,
                                                description: e.target.value,
                                            })
                                        }
                                    />
                                </label>
                                <label>
                                    Deadline:
                                    <input
                                        type="datetime-local"
                                        value={new Date(selectedTask.deadline)
                                            .toISOString()
                                            .slice(0, 16)}
                                        onChange={(e) =>
                                            setSelectedTask({
                                                ...selectedTask,
                                                deadline: e.target.value,
                                            })
                                        }
                                    />
                                </label>
                                <button type="submit">Save</button>
                                <button type="button" onClick={() => setIsEditing(false)}>
                                    Cancel
                                </button>
                            </form>
                        ) : (
                            <>
                                <p><strong>Title:</strong> {selectedTask.title}</p>
                                <p><strong>Description:</strong> {selectedTask.description}</p>
                                <p><strong>Status:</strong> {selectedTask.status === 1 ? "Completed" : "Pending"}</p>
                                <p><strong>Deadline:</strong> {new Date(selectedTask.deadline).toLocaleString()}</p>
                                <p><strong>Created At:</strong> {new Date(selectedTask.created_at).toLocaleString()}</p>
                                <p><strong>Last Modified:</strong> {new Date(selectedTask.updated_at).toLocaleString()}</p>
                                <button onClick={() => setIsEditing(true)}>Edit</button>
                                <button
                                    className="delete-button"
                                    onClick={() => handleDelete(selectedTask.unique_task)}
                                >
                                    ❌ Delete Task
                                </button>
                            </>
                        )}
                        <button className="close-button" onClick={handleCloseDetails}>
                            Close
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

TasksPanel.propTypes = {
    groupId: PropTypes.number.isRequired,
};

export default TasksPanel;
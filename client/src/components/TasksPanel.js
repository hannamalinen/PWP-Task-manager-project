// This file manages the tasks in a group.
// It allows users to view, edit, and delete tasks.
import React, { useEffect, useState } from "react";
import PropTypes from "prop-types"; // Import PropTypes
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import "./TasksPanel.css"; // Import CSS for styling
import API from "../api";

function TasksPanel({ groupId, onEditTask }) {
    const [tasks, setTasks] = useState([]);
    const [completedCount, setCompletedCount] = useState(0); // Count of completed tasks
    const [pendingCount, setPendingCount] = useState(0); // Count of pending tasks

    useEffect(() => {
        // Fetch tasks in the group when the component mounts or groupId changes
        if (groupId) {
            API.get(`/groups/${groupId}/tasks/`)
                .then((response) => {
                    const tasks = response.data || [];
                    setTasks(tasks);

                    // Calculate completed and pending tasks
                    const completed = tasks.filter((task) => task.status === 1).length;
                    const pending = tasks.filter((task) => task.status === 0).length;

                    setCompletedCount(completed);
                    setPendingCount(pending);
                })
                .catch((error) => console.error("Error fetching tasks:", error));
        }
    }, [groupId]);

    const totalTasks = completedCount + pendingCount;

    const handleDelete = (uniqueTask) => {
        if (!window.confirm("Are you sure you want to delete this task?")) return;

        API.delete(`/groups/${groupId}/tasks/${uniqueTask}/`)
            .then(() => {
                setTasks((prevTasks) => {
                    const updatedTasks = prevTasks.filter((task) => task.unique_task !== uniqueTask);

                    // Recalculate completed and pending tasks
                    const completed = updatedTasks.filter((task) => task.status === 1).length;
                    const pending = updatedTasks.filter((task) => task.status === 0).length;

                    setCompletedCount(completed);
                    setPendingCount(pending);

                    return updatedTasks;
                });
            })
            .catch((error) => console.error("Error deleting task:", error));
    };

    return (
        <div className="tasks-panel">
            <h2>Tasks</h2>

            {/* Task Summary Section */}
            <div className="task-summary">
                <h3>Task Overview</h3>
                <div className="circular-progress-container">
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
                </div>
            </div>

            <ul className="task-list">
                {tasks.map((task) => (
                    <li key={task.id} className="task-item">
                        <div className="task-frame">
                            <div className="task-details">
                                <strong>Title:</strong> {task.title} <br />
                                <strong>Description:</strong> {task.description} <br />
                                <strong>Status:</strong> {task.status === 1 ? "Completed" : "Pending"} <br />
                                <strong>Deadline:</strong> {new Date(task.deadline).toLocaleString()} <br />
                                <strong>Created At:</strong> {new Date(task.created_at).toLocaleString()} <br />
                                <strong>Last Modified:</strong> {new Date(task.updated_at).toLocaleString()} <br />
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

// Define PropTypes for the component
TasksPanel.propTypes = {
    groupId: PropTypes.number.isRequired, // groupId must be a number and is required
    onEditTask: PropTypes.func.isRequired, // onEditTask must be a function and is required
};

export default TasksPanel;
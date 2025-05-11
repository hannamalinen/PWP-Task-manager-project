/**
 * This file defines the GroupPage component, which serves as the main page for managing a specific group.
 * It displays the group's tasks, users, and a form for creating or editing tasks.
 */

import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom"; // Add useNavigate for redirection
import TasksPanel from "../components/TasksPanel";
import UsersPanel from "../components/UsersPanel";
import CreateTaskForm from "../components/CreateTaskForm";
import API from "../api";
import "./GroupPage.css";

/**
 * GroupPage component for managing a specific group.
 * Displays the group's tasks, users, and a form for creating or editing tasks.
 */
function GroupPage() {
    const { groupId } = useParams(); // Get the group ID from the URL
    const navigate = useNavigate(); // For redirecting after deletion
    const [groupName, setGroupName] = useState("");
    const [tasks, setTasks] = useState([]);
    const [taskToEdit, setTaskToEdit] = useState(null);

    useEffect(() => {
        // Fetch group details
        API.get(`/groups/${groupId}/`)
            .then((response) => setGroupName(response.data.name))
            .catch((error) => console.error("Error fetching group details:", error));

        // Fetch tasks for the group
        API.get(`/groups/${groupId}/tasks/`)
            .then((response) => setTasks(response.data || []))
            .catch((error) => console.error("Error fetching tasks:", error));
    }, [groupId]);

    /**
     * Handles the deletion of the group.
     * Sends a DELETE request to the backend and redirects to the main page on success.
     */
    const handleDeleteGroup = () => {
        if (!window.confirm("Are you sure you want to delete this group?")) return;

        API.delete(`/groups/${groupId}/`)
            .then(() => {
                alert("Group deleted successfully!");
                navigate("/"); // Redirect to the main page after deletion
            })
            .catch((error) => console.error("Error deleting group:", error));
    };

    const handleTaskCreated = (newTask) => {
        setTasks((prevTasks) => [...prevTasks, newTask]);
    };

    const handleTaskUpdated = (updatedTask) => {
        setTasks((prevTasks) =>
            prevTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task))
        );
    };

    const handleCancelEdit = () => setTaskToEdit(null);

    return (
        <div>
            <div className="group-header">
                <h2 className="group-title">{groupName}</h2>
                <button className="delete-group-button" onClick={handleDeleteGroup}>
                    Delete Group
                </button>
            </div>
            <div className="group-page">
                <div className="panel panel-left">
                    <h3>{taskToEdit ? "Edit Task" : "Create Task"}</h3>
                    <CreateTaskForm
                        groupId={groupId}
                        taskToEdit={taskToEdit}
                        onTaskCreated={handleTaskCreated}
                        onTaskUpdated={handleTaskUpdated}
                        onCancelEdit={handleCancelEdit}
                    />
                </div>
                <div className="panel panel-middle">
                    <TasksPanel
                        groupId={groupId}
                        tasks={tasks}
                        onEditTask={setTaskToEdit}
                    />
                </div>
                <div className="panel panel-right">
                    <UsersPanel groupId={groupId} />
                </div>
            </div>
        </div>
    );
}

export default GroupPage;
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import TasksPanel from "../components/TasksPanel";
import UsersPanel from "../components/UsersPanel";
import CreateTaskForm from "../components/CreateTaskForm";
import API from "../api"; // Add this line
import "./GroupPage.css";

function GroupPage() {
    const { groupId } = useParams();
    const [groupName, setGroupName] = useState("");
    const [tasks, setTasks] = useState([]);
    const [taskToEdit, setTaskToEdit] = useState(null);

    useEffect(() => {
        API.get(`/groups/${groupId}/`)
            .then((response) => setGroupName(response.data.name))
            .catch((error) => console.error("Error fetching group details:", error));

        API.get(`/groups/${groupId}/tasks/`)
            .then((response) => setTasks(response.data || []))
            .catch((error) => console.error("Error fetching tasks:", error));
    }, [groupId]);

    const handleEditTask = (task) => setTaskToEdit(task);
    const handleTaskCreated = (newTask) => {
        console.log("Task created:", newTask); // Log the new task for debugging
        setTasks((prevTasks) => [...prevTasks, newTask]); // Add the new task to the tasks list
    };
    const handleTaskUpdated = (updatedTask) => {
        setTasks((prevTasks) =>
            prevTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task))
        );
    };
    const handleCancelEdit = () => setTaskToEdit(null);

    return (
        <div>
            <h2 className="group-title">{groupName}</h2>
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
                        onEditTask={handleEditTask}
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
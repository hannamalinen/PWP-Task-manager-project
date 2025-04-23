import React, { useState } from "react";
import GroupsPanel from "./components/GroupsPanel";
import TasksPanel from "./components/TasksPanel";
import CreateTaskForm from "./components/CreateTaskForm";
import './App.css';

function App() {
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [tasks, setTasks] = useState([]); // State to manage tasks
    const [taskToEdit, setTaskToEdit] = useState(null);

    const handleTaskCreated = (newTask) => {
        console.log("New task created:", newTask);
        setTasks((prevTasks) => [...prevTasks, newTask]); // Add the new task to the list
    };

    const handleTaskUpdated = (updatedTask) => {
        console.log("Task updated:", updatedTask);
        setTasks((prevTasks) =>
            prevTasks.map((task) =>
                task.id === updatedTask.id ? updatedTask : task
            )
        ); // Update the task in the list
    };

    return (
        <div className="App">
            <h1>Project Management Dashboard</h1>
            <div className="content">
                <GroupsPanel onGroupSelect={setSelectedGroup} />
                {selectedGroup && (
                    <>
                        <TasksPanel
                            groupId={selectedGroup}
                            tasks={tasks}
                            onEditTask={(task) => setTaskToEdit(task)}
                        />
                        <CreateTaskForm
                            groupId={selectedGroup}
                            taskToEdit={taskToEdit}
                            onTaskCreated={handleTaskCreated}
                            onTaskUpdated={handleTaskUpdated}
                        />
                    </>
                )}
            </div>
        </div>
    );
}

export default App;

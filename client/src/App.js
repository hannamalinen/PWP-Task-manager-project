import React, { useState } from "react";
import GroupsPanel from "./components/GroupsPanel";
import TasksPanel from "./components/TasksPanel";
import CreateTaskForm from "./components/CreateTaskForm";
import './App.css';

function App() {
    const [selectedGroup, setSelectedGroup] = useState(null);

    const handleTaskCreated = (newTask) => {
        console.log("New task created:", newTask);
        // Optionally, update the task list in TasksPanel
    };

    return (
        <div className="App">
            <h1>Project Management Dashboard</h1>
            <div className="content">
                <GroupsPanel onGroupSelect={setSelectedGroup} />
                {selectedGroup && (
                    <>
                        <TasksPanel groupId={selectedGroup} />
                        <CreateTaskForm groupId={selectedGroup} onTaskCreated={handleTaskCreated} />
                    </>
                )}
            </div>
        </div>
    );
}

export default App;

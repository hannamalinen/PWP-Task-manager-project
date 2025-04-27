import React, { useState } from "react";
import GroupsPanel from "./components/GroupsPanel";
import TasksPanel from "./components/TasksPanel";
import CreateTaskForm from "./components/CreateTaskForm";
import UsersPanel from "./components/UsersPanel";
import './App.css';

function App() {
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [selectedGroupName, setSelectedGroupName] = useState(""); // Store the group's name
    const [tasks, setTasks] = useState([]);
    const [taskToEdit, setTaskToEdit] = useState(null);

    const handleGroupSelect = (groupId, groupName) => {
        setSelectedGroup(groupId);
        setSelectedGroupName(groupName); // Update the group's name
    };

    return (
        <div className="App">
            <h1>Project Management Dashboard</h1>
            {selectedGroup && (
                <h2>Viewing group: {selectedGroupName}</h2> // Display group name at the top
            )}
            <div className="content">
                <div className="panel">
                    <GroupsPanel onGroupSelect={handleGroupSelect} />
                </div>
                {selectedGroup && (
                    <>
                        <div className="panel">
                            <TasksPanel
                                groupId={selectedGroup}
                                tasks={tasks}
                                onEditTask={(task) => setTaskToEdit(task)}
                            />
                        </div>
                        <div className="panel">
                            <UsersPanel groupId={selectedGroup} />
                        </div>
                        <div className="panel">
                            <CreateTaskForm
                                groupId={selectedGroup}
                                taskToEdit={taskToEdit}
                                onTaskCreated={(newTask) =>
                                    setTasks((prevTasks) => [...prevTasks, newTask])
                                }
                                onTaskUpdated={(updatedTask) =>
                                    setTasks((prevTasks) =>
                                        prevTasks.map((task) =>
                                            task.unique_task === updatedTask.unique_task
                                                ? updatedTask
                                                : task
                                        )
                                    )
                                }
                                onCancelEdit={() => setTaskToEdit(null)}
                            />
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default App;

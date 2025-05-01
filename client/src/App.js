import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import MainPage from "./pages/MainPage";
import ControlPage from "./pages/ControlPage";
import GroupPage from "./pages/GroupPage";
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <header>
                    <h1>Task Manager</h1>
                    <nav>
                        <Link to="/">Main Page</Link>
                        <Link to="/control">Control Page</Link>
                    </nav>
                </header>
                <Routes>
                    <Route path="/" element={<MainPage />} />
                    <Route path="/control" element={<ControlPage />} />
                    <Route path="/group/:groupId" element={<GroupPage />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;

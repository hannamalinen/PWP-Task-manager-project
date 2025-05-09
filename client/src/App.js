import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import MainPage from "./pages/MainPage";
import ControlPage from "./pages/ControlPage";
import GroupPage from "./pages/GroupPage";
import ThemeSwitcher from "./components/ThemeSwitcher"; // Add ThemeSwitcher
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                {/* Theme Switcher */}
                <ThemeSwitcher />
                {/* Header Section */}
                <header className="app-header">
                    <h1>Task Manager</h1>
                    <nav>
                        <Link to="/">Main Page</Link>
                        <Link to="/control">Control Page</Link>
                    </nav>
                </header>



                {/* Main Content Section */}
                <main className="app-content">
                    <Routes>
                        <Route path="/" element={<MainPage />} />
                        <Route path="/control" element={<ControlPage />} />
                        <Route path="/group/:groupId" element={<GroupPage />} />
                    </Routes>
                </main>

                {/* Footer Section */}
                <footer className="app-footer">
                    <p>&copy; 2025 Task Manager. All rights reserved.</p>
                </footer>
            </div>
        </Router>
    );
}

export default App;

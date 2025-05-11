/**
 * This file defines the ThemeSwitcher component, which allows users to switch between different themes.
 * It dynamically updates the CSS variables in the document's root element to apply the selected theme.
 */

import React from "react";
import { themes } from "../themes";

/**
 * ThemeSwitcher component for changing the application's theme.
 */
function ThemeSwitcher() {
    /**
     * Changes the application's theme by updating CSS variables.
     *
     * @param {string} themeName - The name of the theme to apply.
     */
    const changeTheme = (themeName) => {
        const theme = themes[themeName];
        for (const key in theme) {
            document.documentElement.style.setProperty(key, theme[key]);
        }
    };

    return (
        <div className="theme-switcher">
            {/* Buttons for switching themes */}
            <button onClick={() => changeTheme("pink")}>Pink Theme</button>
            <button onClick={() => changeTheme("purple")}>Purple Theme</button>
            <button onClick={() => changeTheme("peach")}>Peach Theme</button>
            <button onClick={() => changeTheme("pastel")}>Pastel Theme</button>
            <button onClick={() => changeTheme("rose")}>Rose Theme</button>
        </div>
    );
}

export default ThemeSwitcher;
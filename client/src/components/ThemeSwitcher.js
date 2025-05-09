import React from "react";
import { themes } from "../themes";

function ThemeSwitcher() {
    const changeTheme = (themeName) => {
        const theme = themes[themeName];
        for (const key in theme) {
            document.documentElement.style.setProperty(key, theme[key]);
        }
    };

    return (
        <div className="theme-switcher">
            <button onClick={() => changeTheme("pink")}>Pink Theme</button>
            <button onClick={() => changeTheme("purple")}>Purple Theme</button>
            <button onClick={() => changeTheme("peach")}>Peach Theme</button>
            <button onClick={() => changeTheme("pastel")}>Pastel Theme</button>
            <button onClick={() => changeTheme("rose")}>Rose Theme</button>
        </div>
    );
}

export default ThemeSwitcher;
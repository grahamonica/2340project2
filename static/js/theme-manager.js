// Code smells refactor #2
class ThemeManager {
    constructor() {
        this.body = document.body;
        // we can easily add more themes if we want
        this.themes = {
            dark: 'dark-mode',
            light: 'light-mode',
            christmas: 'christmas-mode',
            halloween: 'halloween-mode'
        };
        this.initialize();
    }

    initialize() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.setTheme(savedTheme);
        }
 
        // this allows extension to arbitrary themes
        Object.keys(this.themes).forEach(theme => {
            const buttonId = theme === 'dark' || theme === 'light' ? 
                'toggle-dark-light' : `toggle-${theme}`;
            document.getElementById(buttonId)?.addEventListener('click', () => {
                theme === 'dark' || theme === 'light' ? 
                    this.toggleDarkLight() : this.setTheme(theme);
            });
        });
    }

    toggleDarkLight() {
        const newTheme = this.body.classList.contains(this.themes.light) ? 
            'dark' : 'light';
        this.setTheme(newTheme);
    }

    setTheme(themeName) {
        Object.values(this.themes).forEach(theme => 
            this.body.classList.remove(theme)
        );
        this.body.classList.add(this.themes[themeName]);
        localStorage.setItem('theme', themeName);
    }
}

const themeManager = new ThemeManager();
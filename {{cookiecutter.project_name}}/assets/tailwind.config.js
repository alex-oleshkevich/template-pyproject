const defaultTheme = require("tailwindcss/defaultTheme");
const defaultColors = require("tailwindcss/colors");

module.exports = {
    content: ["../{{ cookiecutter.project_name }}/**/*.html", "./js/**/*.ts"],
    plugins: [
        require("@tailwindcss/forms"),
        require("tailwindcss/nesting"),
        require("@tailwindcss/typography"),
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ["Inter", ...defaultTheme.fontFamily.sans],
            },
            colors: {
                accent: defaultColors.blue
            },
        },
    },
};

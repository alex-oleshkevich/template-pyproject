from kupala.routing import Routes, include

routes = Routes(
    [
        include("{{cookiecutter.project_name}}.manage.dashboard.views"),
        include("{{cookiecutter.project_name}}.manage.teams.views"),
    ]
)

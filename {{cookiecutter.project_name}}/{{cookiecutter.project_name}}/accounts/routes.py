from kupala.routing import Routes, include

routes = Routes(
    [
        include("{{cookiecutter.project_name}}.accounts.authentication.views"),
        include("{{cookiecutter.project_name}}.accounts.password_reset.views"),
        include("{{cookiecutter.project_name}}.accounts.registration.views"),
        include("{{cookiecutter.project_name}}.accounts.social.views"),
        include("{{cookiecutter.project_name}}.accounts.profile.views"),
    ]
)

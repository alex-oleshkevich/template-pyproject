from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from {{cookiecutter.project_name}}.config.settings import new_settings_for_test

settings = new_settings_for_test()
engine = create_engine(settings.database.database_url)
Session = scoped_session(sessionmaker(engine))

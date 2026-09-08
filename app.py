from flask import Flask

from config import Config
from extensions import mysql, mail

from routes.home import home_bp
from routes.research import research_bp
from routes.projects import projects_bp
from routes.admin import admin_bp
from routes.technology import technology_bp
from routes.about import about_bp
from routes.contact import contact_bp
from routes.publications import publications_bp
from routes.team import team_bp
from routes.news import news_bp
from routes.team_public import team_public_bp
from routes.publications_public import publications_public_bp
from routes.news_public import news_public_bp

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    mysql.init_app(app)
    mail.init_app(app)

    app.register_blueprint(home_bp)
    app.register_blueprint(research_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(technology_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(publications_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(team_public_bp)
    app.register_blueprint(publications_public_bp)
    app.register_blueprint(news_public_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True
    )
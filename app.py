
from flask import Flask, request
from datetime import datetime

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
from routes.analytics import analytics_bp


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    mysql.init_app(app)
    mail.init_app(app)

    #  
    # REGISTER BLUEPRINTS
    #  

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
    app.register_blueprint(analytics_bp)


    #  
    # GLOBAL PAGE VIEW TRACKING
    #  

    @app.before_request
    def track_page_view():

        # Don't track static files
        if request.path.startswith("/static/"):
            return

        # Don't track admin pages
        if request.path.startswith("/admin"):
            return

        # Don't track OPTIONS requests
        if request.method == "OPTIONS":
            return

        try:

            # Current date and time
            now = datetime.now()

            # Page URL
            page_url = request.path

            # Endpoint
            endpoint = request.endpoint or "unknown"

            # Convert endpoint into readable page name
            page_name = endpoint.split(".")[-1]

            # Special names
            page_names = {
                "home": "Home",
                "research": "Research",
                "research_detail": "Research Detail",
                "projects": "Projects",
                "project_detail": "Project Detail",
                "technology": "Technology",
                "technology_detail": "Technology Detail",
                "about": "About",
                "contact": "Contact",
                "publication_list": "Publications",
                "publication_detail": "Publication Detail",
                "team": "Team",
                "team_detail": "Team Detail",
                "news": "News",
                "news_detail": "News Detail",
            }

            page_name = page_names.get(
                page_name,
                page_name.replace("_", " ").title()
            )


            # Insert page view
            cur = mysql.connection.cursor()

            cur.execute(
                """
                INSERT INTO page_views
                (
                    page_name,
                    page_url,
                    viewed_at,
                    view_day,
                    view_month,
                    view_year
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    page_name,
                    page_url,
                    now,
                    now.date(),
                    now.month,
                    now.year
                )
            )

            mysql.connection.commit()

            cur.close()

        except Exception as e:

            # Analytics failure should NOT break the website
            print(
                "Analytics tracking error:",
                e
            )


    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        debug=True
    )
 

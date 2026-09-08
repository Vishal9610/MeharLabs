from flask import Blueprint, render_template

import MySQLdb.cursors

from extensions import mysql


projects_bp = Blueprint(
    "projects",
    __name__,
    url_prefix="/projects"
)


 
# PROJECT LIST
 

@projects_bp.route("/")
def project_list():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT
            id,
            title,
            slug,
            short_description,
            description,
            category,
            technology,
            status,
            github_url,
            demo_url,
            image,
            featured,
            created_at,
            updated_at
        FROM projects
        ORDER BY created_at DESC
    """)

    projects = cur.fetchall()

    cur.close()

    return render_template(
        "projects/index.html",
        project_list=projects
    )


 
# PROJECT DETAIL
 

@projects_bp.route("/<slug>")
def project_detail(slug):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT
            id,
            title,
            slug,
            short_description,
            description,
            category,
            technology,
            status,
            github_url,
            demo_url,
            image,
            featured,
            created_at,
            updated_at
        FROM projects
        WHERE slug = %s
    """, (slug,))

    project = cur.fetchone()

    cur.close()

    if not project:
        return "Project not found", 404

    return render_template(
        "projects/detail.html",
        project=project
    )
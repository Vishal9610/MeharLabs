from flask import Blueprint, render_template
from extensions import mysql
import MySQLdb.cursors


team_public_bp = Blueprint(
    "team_public",
    __name__,
    url_prefix="/team"
)


@team_public_bp.route("/")
def team():
    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT
            id,
            name,
            designation,
            team_period,
            category,
            bio,
            skills,
            photo,
            linkedin,
            github,
            email,
            display_order
        FROM team
        WHERE status = 1
        ORDER BY
            FIELD(team_period, 'Present', 'Past'),
            category_order DESC,
            display_order ASC,
            id ASC
    """)

    members = cur.fetchall()

    cur.close()

    return render_template(
        "team/index.html",
        members=members
    )
from flask import Blueprint, render_template
from extensions import mysql
import MySQLdb.cursors


publications_public_bp = Blueprint(
    "publications_public",
    __name__,
    url_prefix="/publications"
)


@publications_public_bp.route("/")
def publication_list():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT
            id,
            title,
            authors,
            abstract,
            journal,
            publication_date,
            doi,
            paper_url,
            category,
            image
        FROM publications
        ORDER BY publication_date DESC, id DESC
    """)

    publications = cur.fetchall()

    cur.close()

    return render_template(
        "publications/index.html",
        publications=publications
    )
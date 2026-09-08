from flask import Blueprint, render_template
from extensions import mysql
import MySQLdb.cursors


news_public_bp = Blueprint(
    "news_public",
    __name__,
    url_prefix="/news"
)


@news_public_bp.route("/")
def news_list():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT
            id,
            title,
            short_description,
            content,
            author,
            published_date,
            status,
            featured,
            image
        FROM news
        WHERE status = 'Published'
        ORDER BY published_date DESC, id DESC
    """)

    news = cur.fetchall()

    cur.close()

    return render_template(
        "news/index.html",
        news=news
    )


@news_public_bp.route("/<int:id>")
def news_detail(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT
            id,
            title,
            short_description,
            content,
            author,
            published_date,
            status,
            featured,
            image
        FROM news
        WHERE id = %s
          AND status = 'Published'
    """, (id,))

    item = cur.fetchone()

    cur.close()

    if not item:
        return "News not found", 404

    return render_template(
        "news/detail.html",
        item=item
    )
from flask import Blueprint, render_template
from extensions import mysql
import MySQLdb.cursors


about_bp = Blueprint(
    "about",
    __name__,
    url_prefix="/about"
)


 
# PUBLIC ABOUT PAGE
 

@about_bp.route("/")
def about_page():

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cursor.execute(
        "SELECT * FROM about WHERE id = 1"
    )

    about = cursor.fetchone()

    cursor.close()

    if not about:
        return "About content not found", 404

    return render_template(
        "about/index.html",
        about=about
    )
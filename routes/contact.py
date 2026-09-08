
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from extensions import mysql
import MySQLdb.cursors


contact_bp = Blueprint(
    "contact",
    __name__,
    url_prefix="/contact"
)


 
# CONTACT PAGE + SEND MESSAGE
 

@contact_bp.route("/", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not name or not email or not message:

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return redirect(
                url_for("contact.contact")
            )


        # ----------------------------------------------------
        # INSERT MESSAGE
        # ----------------------------------------------------

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO messages
            (
                name,
                email,
                subject,
                message
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                name,
                email,
                subject,
                message
            )
        )

        mysql.connection.commit()

        cur.close()


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        flash(
            "Your message has been sent successfully.",
            "success"
        )

        return redirect(
            url_for("contact.contact")
        )


    return render_template(
        "contact/index.html"
    )


 
# ADMIN CONTACT MESSAGES
 

@contact_bp.route("/messages")
def contact_list():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute(
        """
        SELECT
            id,
            name,
            email,
            subject,
            message,
            created_at
        FROM messages
        ORDER BY created_at DESC
        """
    )

    messages = cur.fetchall()

    cur.close()

    return render_template(
        "admin/messages.html",
        messages=messages
    )
 

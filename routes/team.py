from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from extensions import mysql
from routes.admin import admin_required

import MySQLdb.cursors
import os

from werkzeug.utils import secure_filename


team_bp = Blueprint(
    "team",
    __name__,
    url_prefix="/admin/team"
)


ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_image(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


 
# TEAM LIST
 

@team_bp.route("/")
@admin_required
def team_list():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT *
        FROM team
        ORDER BY display_order ASC, id ASC
    """)

    members = cur.fetchall()

    cur.close()

    return render_template(
        "admin/team/index.html",
        members=members
    )


 
# ADD TEAM MEMBER
 

@team_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@admin_required
def add_member():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        designation = request.form.get(
            "designation",
            ""
        ).strip()

        bio = request.form.get(
            "bio",
            ""
        ).strip()

        skills = request.form.get(
            "skills",
            ""
        ).strip()

        linkedin = request.form.get(
            "linkedin",
            ""
        ).strip()

        github = request.form.get(
            "github",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        display_order = request.form.get(
            "display_order",
            0
        )

        status = request.form.get(
            "status",
            "Active"
        ).strip()

        if not name:

            flash(
                "Team member name is required.",
                "danger"
            )

            return redirect(
                url_for("team.add_member")
            )

        # IMAGE

        photo_filename = None

        uploaded_photo = request.files.get(
            "photo"
        )

        if uploaded_photo and uploaded_photo.filename:

            if not allowed_image(
                uploaded_photo.filename
            ):

                flash(
                    "Only PNG, JPG, JPEG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for("team.add_member")
                )

            photo_filename = secure_filename(
                uploaded_photo.filename
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "team"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            uploaded_photo.save(
                os.path.join(
                    upload_folder,
                    photo_filename
                )
            )

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO team
            (
                name,
                designation,
                bio,
                skills,
                photo,
                linkedin,
                github,
                email,
                display_order,
                status
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """, (
            name,
            designation,
            bio,
            skills,
            photo_filename,
            linkedin,
            github,
            email,
            display_order,
            status
        ))

        mysql.connection.commit()

        cur.close()

        flash(
            "Team member added successfully.",
            "success"
        )

        return redirect(
            url_for("team.team_list")
        )

    return render_template(
        "admin/team/form.html",
        member=None
    )


 
# EDIT TEAM MEMBER
 

@team_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_member(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT *
        FROM team
        WHERE id = %s
    """, (id,))

    member = cur.fetchone()

    if not member:

        cur.close()

        flash(
            "Team member not found.",
            "danger"
        )

        return redirect(
            url_for("team.team_list")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        designation = request.form.get(
            "designation",
            ""
        ).strip()

        bio = request.form.get(
            "bio",
            ""
        ).strip()

        skills = request.form.get(
            "skills",
            ""
        ).strip()

        linkedin = request.form.get(
            "linkedin",
            ""
        ).strip()

        github = request.form.get(
            "github",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        display_order = request.form.get(
            "display_order",
            0
        )

        status = request.form.get(
            "status",
            "Active"
        ).strip()

        if not name:

            cur.close()

            flash(
                "Team member name is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "team.edit_member",
                    id=id
                )
            )

        photo_filename = member["photo"]

        uploaded_photo = request.files.get(
            "photo"
        )

        if uploaded_photo and uploaded_photo.filename:

            if not allowed_image(
                uploaded_photo.filename
            ):

                cur.close()

                flash(
                    "Only PNG, JPG, JPEG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "team.edit_member",
                        id=id
                    )
                )

            new_filename = secure_filename(
                uploaded_photo.filename
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "team"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            if photo_filename:

                old_path = os.path.join(
                    upload_folder,
                    photo_filename
                )

                if os.path.exists(old_path):

                    os.remove(old_path)

            uploaded_photo.save(
                os.path.join(
                    upload_folder,
                    new_filename
                )
            )

            photo_filename = new_filename

        cur.execute("""
            UPDATE team
            SET
                name = %s,
                designation = %s,
                bio = %s,
                skills = %s,
                photo = %s,
                linkedin = %s,
                github = %s,
                email = %s,
                display_order = %s,
                status = %s
            WHERE id = %s
        """, (
            name,
            designation,
            bio,
            skills,
            photo_filename,
            linkedin,
            github,
            email,
            display_order,
            status,
            id
        ))

        mysql.connection.commit()

        cur.close()

        flash(
            "Team member updated successfully.",
            "success"
        )

        return redirect(
            url_for("team.team_list")
        )

    cur.close()

    return render_template(
        "admin/team/form.html",
        member=member
    )


 
# DELETE TEAM MEMBER
 

@team_bp.route(
    "/delete/<int:id>",
    methods=["POST"]
)
@admin_required
def delete_member(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT photo
        FROM team
        WHERE id = %s
    """, (id,))

    member = cur.fetchone()

    if not member:

        cur.close()

        flash(
            "Team member not found.",
            "danger"
        )

        return redirect(
            url_for("team.team_list")
        )

    cur.execute("""
        DELETE FROM team
        WHERE id = %s
    """, (id,))

    mysql.connection.commit()

    cur.close()

    if member["photo"]:

        photo_path = os.path.join(
            current_app.static_folder,
            "uploads",
            "team",
            member["photo"]
        )

        if os.path.exists(photo_path):

            os.remove(photo_path)

    flash(
        "Team member deleted successfully.",
        "success"
    )

    return redirect(
        url_for("team.team_list")
    )
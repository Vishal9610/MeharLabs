
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


  
# ALLOWED IMAGE EXTENSIONS
  

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
        ORDER BY
            FIELD(team_period, 'Present', 'Past'),
            category ASC,
            display_order ASC,
            id ASC
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

          
        # BASIC INFORMATION
          

        name = request.form.get(
            "name",
            ""
        ).strip()

        designation = request.form.get(
            "designation",
            ""
        ).strip()

          
        # TEAM PERIOD
        # Present / Past
          

        team_period = request.form.get(
            "team_period",
            "Present"
        ).strip()

          
        # CATEGORY
          

        category = request.form.get(
            "category",
            "Other"
        ).strip()

          
        # BIO
          

        bio = request.form.get(
            "bio",
            ""
        ).strip()

          
        # SKILLS
          

        skills = request.form.get(
            "skills",
            ""
        ).strip()

          
        # CONTACT / SOCIAL
          

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

          
        # DISPLAY ORDER
          

        try:
            display_order = int(
                request.form.get(
                    "display_order",
                    0
                )
            )
        except (TypeError, ValueError):

            display_order = 0

          
        # STATUS
        # Database: tinyint(1)
        # Active = 1
        # Inactive = 0
          

        status_value = request.form.get(
            "status",
            "1"
        ).strip()

        if status_value in ("1", "Active", "active"):
            status = 1
        else:
            status = 0

          
        # VALIDATION
          

        if not name:

            flash(
                "Team member name is required.",
                "danger"
            )

            return redirect(
                url_for("team.add_member")
            )

          
        # VALIDATE TEAM PERIOD
          

        if team_period not in (
            "Present",
            "Past"
        ):

            team_period = "Present"

          
        # IMAGE UPLOAD
          

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

          
        # INSERT
          

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO team
            (
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
                display_order,
                status
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """, (
            name,
            designation,
            team_period,
            category,
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

      
    # GET
      

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

      
    # GET EXISTING MEMBER
      

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

      
    # POST
      

    if request.method == "POST":

          
        # BASIC INFORMATION
          

        name = request.form.get(
            "name",
            ""
        ).strip()

        designation = request.form.get(
            "designation",
            ""
        ).strip()

          
        # TEAM PERIOD
          

        team_period = request.form.get(
            "team_period",
            "Present"
        ).strip()

          
        # CATEGORY
          

        category = request.form.get(
            "category",
            "Other"
        ).strip()

          
        # BIO
          

        bio = request.form.get(
            "bio",
            ""
        ).strip()

          
        # SKILLS
          

        skills = request.form.get(
            "skills",
            ""
        ).strip()

          
        # CONTACT / SOCIAL
          

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

          
        # DISPLAY ORDER
          

        try:
            display_order = int(
                request.form.get(
                    "display_order",
                    0
                )
            )
        except (TypeError, ValueError):

            display_order = 0

          
        # STATUS
        # tinyint(1)
          

        status_value = request.form.get(
            "status",
            "1"
        ).strip()

        if status_value in (
            "1",
            "Active",
            "active"
        ):

            status = 1

        else:

            status = 0

          
        # VALIDATION
          

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

          
        # VALIDATE TEAM PERIOD
          

        if team_period not in (
            "Present",
            "Past"
        ):

            team_period = "Present"

          
        # EXISTING PHOTO
          

        photo_filename = member["photo"]

        uploaded_photo = request.files.get(
            "photo"
        )

          
        # NEW PHOTO
          

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

              
            # DELETE OLD PHOTO
              

            if photo_filename:

                old_path = os.path.join(
                    upload_folder,
                    photo_filename
                )

                if os.path.exists(old_path):

                    os.remove(old_path)

              
            # SAVE NEW PHOTO
              

            uploaded_photo.save(
                os.path.join(
                    upload_folder,
                    new_filename
                )
            )

            photo_filename = new_filename

          
        # UPDATE
          

        cur.execute("""
            UPDATE team
            SET
                name = %s,
                designation = %s,
                team_period = %s,
                category = %s,
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
            team_period,
            category,
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

      
    # GET
      

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

      
    # GET PHOTO
      

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

      
    # DELETE DATABASE RECORD
      

    cur.execute("""
        DELETE FROM team
        WHERE id = %s
    """, (id,))

    mysql.connection.commit()

    cur.close()

      
    # DELETE PHOTO
      

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
  

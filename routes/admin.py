from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from functools import wraps

import random
import time
import os
import re

import MySQLdb
import MySQLdb.cursors

from werkzeug.utils import secure_filename

from extensions import mysql, mail
from flask_mail import Message


# ============================================================
# ADMIN BLUEPRINT
# ============================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def admin_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(
                url_for("admin.login")
            )

        return view(*args, **kwargs)

    return wrapped_view


# ============================================================
# NORMAL PASSWORD LOGIN
# ============================================================

@admin_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == "admin"
            and password == "admin123"
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin.dashboard")
            )

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template(
        "admin/login.html"
    )


# ============================================================
# EMAIL OTP LOGIN
# ============================================================

@admin_bp.route(
    "/login-otp",
    methods=["GET", "POST"]
)
def login_otp():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        if not email:

            flash(
                "loveindiabyvishal9616@gmail.com",
                "danger"
            )

            return redirect(
                url_for("admin.login_otp")
            )

        # ----------------------------------------------------
        # Registered admin email
        # ----------------------------------------------------

        registered_email = current_app.config.get(
            "ADMIN_EMAIL",
            "loveindiabyvishal9616@gmail.com"
        ).strip().lower()

        if email != registered_email:

            flash(
                "Email not registered.",
                "error"
            )

            return render_template(
                "admin/login_otp.html"
            )

        # ----------------------------------------------------
        # Generate OTP
        # ----------------------------------------------------

        otp = str(
            random.randint(
                100000,
                999999
            )
        )

        session["admin_otp"] = otp
        session["admin_otp_email"] = email
        session["admin_otp_time"] = time.time()

        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        try:

            msg = Message(
                subject="MeharLabs Admin Login OTP",
                sender=current_app.config.get(
                    "MAIL_DEFAULT_SENDER"
                ),
                recipients=[email]
            )

            msg.body = f"""
Hello,

Your MeharLabs Admin Login OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this OTP, please ignore this email.

Regards,
MeharLabs
"""

            mail.send(msg)

            flash(
                "OTP has been sent to your email.",
                "success"
            )

            return redirect(
                url_for("admin.verify_otp")
            )

        except Exception as e:

            print(
                "EMAIL ERROR:",
                e
            )

            flash(
                "Unable to send OTP. Please check email configuration.",
                "danger"
            )

    return render_template(
        "admin/login_otp.html"
    )


# ============================================================
# VERIFY EMAIL OTP
# ============================================================

@admin_bp.route(
    "/verify-otp",
    methods=["GET", "POST"]
)
def verify_otp():

    if not session.get("admin_otp"):

        flash(
            "Please request a new OTP.",
            "danger"
        )

        return redirect(
            url_for("admin.login_otp")
        )

    if request.method == "POST":

        entered_otp = request.form.get(
            "otp",
            ""
        ).strip()

        saved_otp = session.get(
            "admin_otp"
        )

        otp_time = session.get(
            "admin_otp_time"
        )

        # ----------------------------------------------------
        # OTP expiry - 5 minutes
        # ----------------------------------------------------

        if (
            not otp_time
            or time.time() - otp_time > 300
        ):

            session.pop(
                "admin_otp",
                None
            )

            session.pop(
                "admin_otp_email",
                None
            )

            session.pop(
                "admin_otp_time",
                None
            )

            flash(
                "OTP has expired. Please request a new OTP.",
                "danger"
            )

            return redirect(
                url_for("admin.login_otp")
            )

        # ----------------------------------------------------
        # Check OTP
        # ----------------------------------------------------

        if entered_otp != saved_otp:

            flash(
                "Invalid OTP.",
                "danger"
            )

            return redirect(
                url_for("admin.verify_otp")
            )

        # ----------------------------------------------------
        # Login successful
        # ----------------------------------------------------

        session["admin_logged_in"] = True

        session.pop(
            "admin_otp",
            None
        )

        session.pop(
            "admin_otp_email",
            None
        )

        session.pop(
            "admin_otp_time",
            None
        )

        flash(
            "Login successful.",
            "success"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    return render_template(
        "admin/verify_otp.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@admin_bp.route(
    "/dashboard"
)
@admin_required
def dashboard():

    return render_template(
        "admin/dashboard.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@admin_bp.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for("admin.login")
    )


# ============================================================
# IMAGE SETTINGS
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_image(filename):

    return (
        "."
        in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


# ============================================================
# PROJECT MANAGEMENT
# ============================================================

@admin_bp.route(
    "/projects"
)
@admin_required
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
        "admin/projects/index.html",
        projects=projects
    )


# ============================================================
# ADD PROJECT
# ============================================================

@admin_bp.route(
    "/projects/add",
    methods=["GET", "POST"]
)
@admin_required
def add_project():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        technology = request.form.get(
            "technology",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Development"
        ).strip()

        github_url = request.form.get(
            "github_url",
            ""
        ).strip()

        demo_url = request.form.get(
            "demo_url",
            ""
        ).strip()

        featured = (
            1
            if request.form.get("featured")
            else 0
        )

        image = request.files.get(
            "image"
        )

        image_name = None

        # ----------------------------------------------------
        # Validate title
        # ----------------------------------------------------

        if not title:

            flash(
                "Project title is required.",
                "danger"
            )

            return redirect(
                url_for("admin.add_project")
            )

        # ----------------------------------------------------
        # Generate slug
        # ----------------------------------------------------

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            title.lower()
        ).strip("-")

        if not slug:

            flash(
                "Please enter a valid project title.",
                "danger"
            )

            return redirect(
                url_for("admin.add_project")
            )

        # ----------------------------------------------------
        # Image upload
        # ----------------------------------------------------

        if image and image.filename:

            if not allowed_image(
                image.filename
            ):

                flash(
                    "Only PNG, JPG, JPEG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for("admin.add_project")
                )

            image_name = secure_filename(
                image.filename
            )

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "projects"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            image.save(
                os.path.join(
                    upload_folder,
                    image_name
                )
            )

        # ----------------------------------------------------
        # Database
        # ----------------------------------------------------

        cur = mysql.connection.cursor()

        original_slug = slug
        counter = 2

        while True:

            cur.execute(
                """
                SELECT id
                FROM projects
                WHERE slug = %s
                """,
                (slug,)
            )

            existing = cur.fetchone()

            if not existing:
                break

            slug = (
                f"{original_slug}-{counter}"
            )

            counter += 1

        # ----------------------------------------------------
        # Insert
        # ----------------------------------------------------

        cur.execute(
            """
            INSERT INTO projects
            (
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
                featured
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                title,
                slug,
                short_description,
                description,
                category,
                technology,
                status,
                github_url,
                demo_url,
                image_name,
                featured
            )
        )

        mysql.connection.commit()

        cur.close()

        flash(
            "Project added successfully.",
            "success"
        )

        return redirect(
            url_for("admin.project_list")
        )

    return render_template(
        "admin/projects/form.html",
        project=None
    )


# ============================================================
# EDIT PROJECT
# ============================================================

@admin_bp.route(
    "/projects/edit/<int:id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_project(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute(
        """
        SELECT *
        FROM projects
        WHERE id = %s
        """,
        (id,)
    )

    project = cur.fetchone()

    if project is None:

        cur.close()

        flash(
            "Project not found.",
            "error"
        )

        return redirect(
            url_for("admin.project_list")
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        technology = request.form.get(
            "technology",
            ""
        ).strip()

        status = request.form.get(
            "status",
            ""
        ).strip()

        github_url = request.form.get(
            "github_url",
            ""
        ).strip()

        demo_url = request.form.get(
            "demo_url",
            ""
        ).strip()

        featured = (
            1
            if request.form.get("featured")
            else 0
        )

        image = request.files.get(
            "image"
        )

        image_name = project["image"]

        # ----------------------------------------------------
        # New image
        # ----------------------------------------------------

        if image and image.filename:

            if not allowed_image(
                image.filename
            ):

                cur.close()

                flash(
                    "Only PNG, JPG, JPEG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "admin.edit_project",
                        id=id
                    )
                )

            filename = secure_filename(
                image.filename
            )

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "projects"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            image.save(
                os.path.join(
                    upload_folder,
                    filename
                )
            )

            image_name = filename

        # ----------------------------------------------------
        # Update
        # ----------------------------------------------------

        cur.execute(
            """
            UPDATE projects
            SET
                title = %s,
                slug = %s,
                short_description = %s,
                description = %s,
                category = %s,
                technology = %s,
                status = %s,
                github_url = %s,
                demo_url = %s,
                image = %s,
                featured = %s
            WHERE id = %s
            """,
            (
                title,
                slug,
                short_description,
                description,
                category,
                technology,
                status,
                github_url,
                demo_url,
                image_name,
                featured,
                id
            )
        )

        mysql.connection.commit()

        cur.close()

        flash(
            "Project updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.project_list")
        )

    cur.close()

    return render_template(
        "admin/projects/form.html",
        project=project
    )


# ============================================================
# DELETE PROJECT
# ============================================================

@admin_bp.route(
    "/projects/delete/<int:id>",
    methods=["POST"]
)
@admin_required
def delete_project(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute(
        """
        SELECT image
        FROM projects
        WHERE id = %s
        """,
        (id,)
    )

    project = cur.fetchone()

    if not project:

        cur.close()

        flash(
            "Project not found.",
            "error"
        )

        return redirect(
            url_for("admin.project_list")
        )

    image = project["image"]

    cur.execute(
        """
        DELETE FROM projects
        WHERE id = %s
        """,
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    if image:

        image_path = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
            "projects",
            image
        )

        if os.path.exists(
            image_path
        ):
            os.remove(
                image_path
            )

    flash(
        "Project deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.project_list")
    )


# ============================================================
# RESEARCH MANAGEMENT
# ============================================================

@admin_bp.route(
    "/research"
)
@admin_required
def research_list():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT
            id,
            title,
            short_description,
            research_area,
            technology,
            status,
            image,
            featured
        FROM research
        ORDER BY id DESC
    """)

    research = cur.fetchall()

    cur.close()

    return render_template(
        "admin/research/index.html",
        research=research
    )


# ============================================================
# ADD RESEARCH
# ============================================================

@admin_bp.route(
    "/research/add",
    methods=["GET", "POST"]
)
@admin_required
def research_add():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        research_area = request.form.get(
            "research_area",
            ""
        ).strip()

        technology = request.form.get(
            "technology",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Research"
        ).strip()

        featured = (
            1
            if request.form.get("featured")
            else 0
        )

        if not title:

            flash(
                "Research title is required.",
                "danger"
            )

            return redirect(
                url_for("admin.research_add")
            )

        # ----------------------------------------------------
        # Slug
        # ----------------------------------------------------

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            title.lower()
        ).strip("-")

        if not slug:
            slug = "research"

        cur = mysql.connection.cursor()

        original_slug = slug
        counter = 2

        while True:

            cur.execute(
                """
                SELECT id
                FROM research
                WHERE slug = %s
                """,
                (slug,)
            )

            existing = cur.fetchone()

            if not existing:
                break

            slug = (
                f"{original_slug}-{counter}"
            )

            counter += 1

        # ----------------------------------------------------
        # Image
        # ----------------------------------------------------

        image_filename = None

        uploaded_image = request.files.get(
            "image"
        )

        if (
            uploaded_image
            and uploaded_image.filename
        ):

            if not allowed_image(
                uploaded_image.filename
            ):

                cur.close()

                flash(
                    "Only PNG, JPG, JPEG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for("admin.research_add")
                )

            image_filename = secure_filename(
                uploaded_image.filename
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "research"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            uploaded_image.save(
                os.path.join(
                    upload_folder,
                    image_filename
                )
            )

        # ----------------------------------------------------
        # Insert
        # ----------------------------------------------------

        cur.execute(
            """
            INSERT INTO research
            (
                title,
                slug,
                short_description,
                description,
                research_area,
                technology,
                status,
                image,
                featured
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            (
                title,
                slug,
                short_description,
                description,
                research_area,
                technology,
                status,
                image_filename,
                featured
            )
        )

        mysql.connection.commit()

        cur.close()

        flash(
            "Research added successfully.",
            "success"
        )

        return redirect(
            url_for("admin.research_list")
        )

    return render_template(
        "admin/research/add.html"
    )


# ============================================================
# EDIT RESEARCH
# ============================================================

@admin_bp.route(
    "/research/edit/<int:id>",
    methods=["GET", "POST"]
)
@admin_required
def research_edit(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute(
        """
        SELECT
            id,
            title,
            slug,
            short_description,
            description,
            research_area,
            technology,
            status,
            image,
            featured,
            created_at,
            updated_at
        FROM research
        WHERE id = %s
        """,
        (id,)
    )

    item = cur.fetchone()

    if not item:

        cur.close()

        flash(
            "Research not found.",
            "danger"
        )

        return redirect(
            url_for("admin.research_list")
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        research_area = request.form.get(
            "research_area",
            ""
        ).strip()

        technology = request.form.get(
            "technology",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Research"
        ).strip()

        featured = (
            1
            if request.form.get("featured")
            else 0
        )

        if not title:

            cur.close()

            flash(
                "Research title is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "admin.research_edit",
                    id=id
                )
            )

        # ----------------------------------------------------
        # Slug
        # ----------------------------------------------------

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            title.lower()
        ).strip("-")

        if not slug:
            slug = "research"

        original_slug = slug
        counter = 2

        while True:

            cur.execute(
                """
                SELECT id
                FROM research
                WHERE slug = %s
                AND id != %s
                """,
                (
                    slug,
                    id
                )
            )

            existing = cur.fetchone()

            if not existing:
                break

            slug = (
                f"{original_slug}-{counter}"
            )

            counter += 1

        # ----------------------------------------------------
        # Existing image
        # ----------------------------------------------------

        image_filename = item["image"]

        uploaded_image = request.files.get(
            "image"
        )

        if (
            uploaded_image
            and uploaded_image.filename
        ):

            if not allowed_image(
                uploaded_image.filename
            ):

                cur.close()

                flash(
                    "Only PNG, JPG, JPEG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "admin.research_edit",
                        id=id
                    )
                )

            new_filename = secure_filename(
                uploaded_image.filename
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "research"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            if image_filename:

                old_image_path = os.path.join(
                    upload_folder,
                    image_filename
                )

                if os.path.exists(
                    old_image_path
                ):

                    os.remove(
                        old_image_path
                    )

            uploaded_image.save(
                os.path.join(
                    upload_folder,
                    new_filename
                )
            )

            image_filename = new_filename

        # ----------------------------------------------------
        # Update
        # ----------------------------------------------------

        cur.execute(
            """
            UPDATE research
            SET
                title = %s,
                slug = %s,
                short_description = %s,
                description = %s,
                research_area = %s,
                technology = %s,
                status = %s,
                image = %s,
                featured = %s
            WHERE id = %s
            """,
            (
                title,
                slug,
                short_description,
                description,
                research_area,
                technology,
                status,
                image_filename,
                featured,
                id
            )
        )

        mysql.connection.commit()

        cur.close()

        flash(
            "Research updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.research_list")
        )

    cur.close()

    return render_template(
        "admin/research/edit.html",
        item=item
    )


# ============================================================
# DELETE RESEARCH
# ============================================================

@admin_bp.route(
    "/research/delete/<int:id>",
    methods=["POST"]
)
@admin_required
def research_delete(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute(
        """
        SELECT image
        FROM research
        WHERE id = %s
        """,
        (id,)
    )

    item = cur.fetchone()

    if not item:

        cur.close()

        flash(
            "Research not found.",
            "error"
        )

        return redirect(
            url_for("admin.research_list")
        )

    image = item["image"]

    cur.execute(
        """
        DELETE FROM research
        WHERE id = %s
        """,
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    if image:

        image_path = os.path.join(
            current_app.static_folder,
            "uploads",
            "research",
            image
        )

        if os.path.exists(
            image_path
        ):

            os.remove(
                image_path
            )

    flash(
        "Research deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.research_list")
    )


# ============================================================
# ABOUT MANAGEMENT
# ============================================================

@admin_bp.route(
    "/about/",
    methods=["GET", "POST"]
)
@admin_required
def about_list():

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    if request.method == "POST":

        hero_eyebrow = request.form.get(
            "hero_eyebrow"
        )

        hero_title = request.form.get(
            "hero_title"
        )

        hero_description = request.form.get(
            "hero_description"
        )

        who_eyebrow = request.form.get(
            "who_eyebrow"
        )

        who_title = request.form.get(
            "who_title"
        )

        who_description = request.form.get(
            "who_description"
        )

        mission_eyebrow = request.form.get(
            "mission_eyebrow"
        )

        mission_title = request.form.get(
            "mission_title"
        )

        mission_description = request.form.get(
            "mission_description"
        )

        vision_eyebrow = request.form.get(
            "vision_eyebrow"
        )

        vision_title = request.form.get(
            "vision_title"
        )

        vision_description = request.form.get(
            "vision_description"
        )

        focus_eyebrow = request.form.get(
            "focus_eyebrow"
        )

        focus_title = request.form.get(
            "focus_title"
        )

        focus_description = request.form.get(
            "focus_description"
        )

        area1_title = request.form.get(
            "area1_title"
        )

        area1_description = request.form.get(
            "area1_description"
        )

        area2_title = request.form.get(
            "area2_title"
        )

        area2_description = request.form.get(
            "area2_description"
        )

        area3_title = request.form.get(
            "area3_title"
        )

        area3_description = request.form.get(
            "area3_description"
        )

        area4_title = request.form.get(
            "area4_title"
        )

        area4_description = request.form.get(
            "area4_description"
        )

        cta_eyebrow = request.form.get(
            "cta_eyebrow"
        )

        cta_title = request.form.get(
            "cta_title"
        )

        cta_description = request.form.get(
            "cta_description"
        )

        cta_button_text = request.form.get(
            "cta_button_text"
        )

        cursor.execute(
            """
            UPDATE about
            SET
                hero_eyebrow=%s,
                hero_title=%s,
                hero_description=%s,

                who_eyebrow=%s,
                who_title=%s,
                who_description=%s,

                mission_eyebrow=%s,
                mission_title=%s,
                mission_description=%s,

                vision_eyebrow=%s,
                vision_title=%s,
                vision_description=%s,

                focus_eyebrow=%s,
                focus_title=%s,
                focus_description=%s,

                area1_title=%s,
                area1_description=%s,

                area2_title=%s,
                area2_description=%s,

                area3_title=%s,
                area3_description=%s,

                area4_title=%s,
                area4_description=%s,

                cta_eyebrow=%s,
                cta_title=%s,
                cta_description=%s,
                cta_button_text=%s

            WHERE id=1
            """,
            (
                hero_eyebrow,
                hero_title,
                hero_description,

                who_eyebrow,
                who_title,
                who_description,

                mission_eyebrow,
                mission_title,
                mission_description,

                vision_eyebrow,
                vision_title,
                vision_description,

                focus_eyebrow,
                focus_title,
                focus_description,

                area1_title,
                area1_description,

                area2_title,
                area2_description,

                area3_title,
                area3_description,

                area4_title,
                area4_description,

                cta_eyebrow,
                cta_title,
                cta_description,
                cta_button_text
            )
        )

        mysql.connection.commit()

        cursor.close()

        flash(
            "About page updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.about_list")
        )

    cursor.execute(
        """
        SELECT *
        FROM about
        WHERE id=1
        """
    )

    about = cursor.fetchone()

    cursor.close()

    return render_template(
        "admin/about/index.html",
        about=about
    )


# ============================================================
# CONTACT MESSAGES
# ============================================================

@admin_bp.route(
    "/messages"
)
@admin_required
def messages():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute(
        """
        SELECT *
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
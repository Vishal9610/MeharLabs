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
import re

from werkzeug.utils import secure_filename


news_bp = Blueprint(
    "news",
    __name__,
    url_prefix="/admin/news"
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


 
# NEWS LIST
 

@news_bp.route("/")
@admin_required
def news_list():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT *
        FROM news
        ORDER BY published_date DESC, id DESC
    """)

    news = cur.fetchall()

    cur.close()

    return render_template(
        "admin/news/index.html",
        news=news
    )


 
# ADD NEWS
 

@news_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@admin_required
def add_news():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()

        author = request.form.get(
            "author",
            ""
        ).strip()

        published_date = request.form.get(
            "published_date"
        ) or None

        status = request.form.get(
            "status",
            "Draft"
        ).strip()

        featured = (
            1
            if request.form.get("featured")
            else 0
        )

        if not title:

            flash(
                "News title is required.",
                "danger"
            )

            return redirect(
                url_for("news.add_news")
            )

        # --------------------------------
        # SLUG
        # --------------------------------

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            title.lower()
        ).strip("-")

        if not slug:

            slug = "news"

        cur = mysql.connection.cursor()

        original_slug = slug
        counter = 2

        while True:

            cur.execute("""
                SELECT id
                FROM news
                WHERE slug = %s
            """, (slug,))

            existing = cur.fetchone()

            if not existing:
                break

            slug = f"{original_slug}-{counter}"

            counter += 1

        # --------------------------------
        # IMAGE
        # --------------------------------

        image_filename = None

        uploaded_image = request.files.get(
            "image"
        )

        if uploaded_image and uploaded_image.filename:

            if not allowed_image(
                uploaded_image.filename
            ):

                cur.close()

                flash(
                    "Only PNG, JPG, JPEG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for("news.add_news")
                )

            image_filename = secure_filename(
                uploaded_image.filename
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "news"
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

        # --------------------------------
        # INSERT
        # --------------------------------

        cur.execute("""
            INSERT INTO news
            (
                title,
                slug,
                short_description,
                content,
                image,
                author,
                published_date,
                featured,
                status
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, (
            title,
            slug,
            short_description,
            content,
            image_filename,
            author,
            published_date,
            featured,
            status
        ))

        mysql.connection.commit()

        cur.close()

        flash(
            "News added successfully.",
            "success"
        )

        return redirect(
            url_for("news.news_list")
        )

    return render_template(
        "admin/news/form.html",
        item=None
    )


 
# EDIT NEWS
 

@news_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_news(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT *
        FROM news
        WHERE id = %s
    """, (id,))

    item = cur.fetchone()

    if not item:

        cur.close()

        flash(
            "News not found.",
            "danger"
        )

        return redirect(
            url_for("news.news_list")
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

        content = request.form.get(
            "content",
            ""
        ).strip()

        author = request.form.get(
            "author",
            ""
        ).strip()

        published_date = request.form.get(
            "published_date"
        ) or None

        status = request.form.get(
            "status",
            "Draft"
        ).strip()

        featured = (
            1
            if request.form.get("featured")
            else 0
        )

        if not title:

            cur.close()

            flash(
                "News title is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "news.edit_news",
                    id=id
                )
            )

        # --------------------------------
        # SLUG
        # --------------------------------

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            title.lower()
        ).strip("-")

        if not slug:
            slug = "news"

        original_slug = slug
        counter = 2

        while True:

            cur.execute("""
                SELECT id
                FROM news
                WHERE slug = %s
                AND id != %s
            """, (
                slug,
                id
            ))

            existing = cur.fetchone()

            if not existing:
                break

            slug = f"{original_slug}-{counter}"

            counter += 1

        # --------------------------------
        # IMAGE
        # --------------------------------

        image_filename = item["image"]

        uploaded_image = request.files.get(
            "image"
        )

        if uploaded_image and uploaded_image.filename:

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
                        "news.edit_news",
                        id=id
                    )
                )

            new_filename = secure_filename(
                uploaded_image.filename
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "news"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            if image_filename:

                old_path = os.path.join(
                    upload_folder,
                    image_filename
                )

                if os.path.exists(old_path):

                    os.remove(old_path)

            uploaded_image.save(
                os.path.join(
                    upload_folder,
                    new_filename
                )
            )

            image_filename = new_filename

        # --------------------------------
        # UPDATE
        # --------------------------------

        cur.execute("""
            UPDATE news
            SET
                title = %s,
                slug = %s,
                short_description = %s,
                content = %s,
                image = %s,
                author = %s,
                published_date = %s,
                featured = %s,
                status = %s
            WHERE id = %s
        """, (
            title,
            slug,
            short_description,
            content,
            image_filename,
            author,
            published_date,
            featured,
            status,
            id
        ))

        mysql.connection.commit()

        cur.close()

        flash(
            "News updated successfully.",
            "success"
        )

        return redirect(
            url_for("news.news_list")
        )

    cur.close()

    return render_template(
        "admin/news/form.html",
        item=item
    )


 
# DELETE NEWS
 

@news_bp.route(
    "/delete/<int:id>",
    methods=["POST"]
)
@admin_required
def delete_news(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT image
        FROM news
        WHERE id = %s
    """, (id,))

    item = cur.fetchone()

    if not item:

        cur.close()

        flash(
            "News not found.",
            "danger"
        )

        return redirect(
            url_for("news.news_list")
        )

    cur.execute("""
        DELETE FROM news
        WHERE id = %s
    """, (id,))

    mysql.connection.commit()

    cur.close()

    if item["image"]:

        image_path = os.path.join(
            current_app.static_folder,
            "uploads",
            "news",
            item["image"]
        )

        if os.path.exists(image_path):

            os.remove(image_path)

    flash(
        "News deleted successfully.",
        "success"
    )

    return redirect(
        url_for("news.news_list")
    )
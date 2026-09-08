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


publications_bp = Blueprint(
    "publications",
    __name__,
    url_prefix="/admin/publications"
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


 
# PUBLICATIONS LIST
 

@publications_bp.route("/")
@admin_required
def publication_list():

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT
            id,
            title,
            authors,
            journal,
            publication_date,
            doi,
            paper_url,
            category,
            image,
            created_at
        FROM publications
        ORDER BY publication_date DESC, id DESC
    """)

    publications = cur.fetchall()

    cur.close()

    return render_template(
        "admin/publications/index.html",
        publications=publications
    )


 
# ADD PUBLICATION
 

@publications_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@admin_required
def add_publication():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        authors = request.form.get(
            "authors",
            ""
        ).strip()

        abstract = request.form.get(
            "abstract",
            ""
        ).strip()

        journal = request.form.get(
            "journal",
            ""
        ).strip()

        publication_date = request.form.get(
            "publication_date"
        ) or None

        doi = request.form.get(
            "doi",
            ""
        ).strip()

        paper_url = request.form.get(
            "paper_url",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        if not title:

            flash(
                "Publication title is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "publications.add_publication"
                )
            )

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

                flash(
                    "Only PNG, JPG, JPEG and WEBP images are allowed.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "publications.add_publication"
                    )
                )

            image_filename = secure_filename(
                uploaded_image.filename
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "publications"
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
        # DATABASE
        # --------------------------------

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO publications
            (
                title,
                authors,
                abstract,
                journal,
                publication_date,
                doi,
                paper_url,
                category,
                image
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, (
            title,
            authors,
            abstract,
            journal,
            publication_date,
            doi,
            paper_url,
            category,
            image_filename
        ))

        mysql.connection.commit()

        cur.close()

        flash(
            "Publication added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "publications.publication_list"
            )
        )

    return render_template(
        "admin/publications/form.html",
        publication=None
    )


 
# EDIT PUBLICATION
 

@publications_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_publication(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT *
        FROM publications
        WHERE id = %s
    """, (id,))

    publication = cur.fetchone()

    if not publication:

        cur.close()

        flash(
            "Publication not found.",
            "danger"
        )

        return redirect(
            url_for(
                "publications.publication_list"
            )
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        authors = request.form.get(
            "authors",
            ""
        ).strip()

        abstract = request.form.get(
            "abstract",
            ""
        ).strip()

        journal = request.form.get(
            "journal",
            ""
        ).strip()

        publication_date = request.form.get(
            "publication_date"
        ) or None

        doi = request.form.get(
            "doi",
            ""
        ).strip()

        paper_url = request.form.get(
            "paper_url",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        if not title:

            cur.close()

            flash(
                "Publication title is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "publications.edit_publication",
                    id=id
                )
            )

        image_filename = publication["image"]

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
                        "publications.edit_publication",
                        id=id
                    )
                )

            new_filename = secure_filename(
                uploaded_image.filename
            )

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "publications"
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

        cur.execute("""
            UPDATE publications
            SET
                title = %s,
                authors = %s,
                abstract = %s,
                journal = %s,
                publication_date = %s,
                doi = %s,
                paper_url = %s,
                category = %s,
                image = %s
            WHERE id = %s
        """, (
            title,
            authors,
            abstract,
            journal,
            publication_date,
            doi,
            paper_url,
            category,
            image_filename,
            id
        ))

        mysql.connection.commit()

        cur.close()

        flash(
            "Publication updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "publications.publication_list"
            )
        )

    cur.close()

    return render_template(
        "admin/publications/form.html",
        publication=publication
    )


 
# DELETE PUBLICATION
 

@publications_bp.route(
    "/delete/<int:id>",
    methods=["POST"]
)
@admin_required
def delete_publication(id):

    cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cur.execute("""
        SELECT image
        FROM publications
        WHERE id = %s
    """, (id,))

    publication = cur.fetchone()

    if not publication:

        cur.close()

        flash(
            "Publication not found.",
            "danger"
        )

        return redirect(
            url_for(
                "publications.publication_list"
            )
        )

    cur.execute("""
        DELETE FROM publications
        WHERE id = %s
    """, (id,))

    mysql.connection.commit()

    cur.close()

    if publication["image"]:

        image_path = os.path.join(
            current_app.static_folder,
            "uploads",
            "publications",
            publication["image"]
        )

        if os.path.exists(image_path):

            os.remove(image_path)

    flash(
        "Publication deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "publications.publication_list"
        )
    )
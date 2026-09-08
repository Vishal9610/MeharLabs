from flask import Blueprint, render_template

from extensions import mysql


technology_bp = Blueprint(
    "technology",
    __name__,
    url_prefix="/technology"
)


# =========================
# TECHNOLOGY LIST
# =========================

@technology_bp.route("/")
def technology_list():

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            id,
            title,
            slug,
            short_description,
            description,
            technology,
            applications,
            research_direction,
            image,
            featured,
            created_at,
            updated_at
        FROM technologies
        ORDER BY created_at ASC
    """)

    rows = cur.fetchall()

    cur.close()

    technologies = []

    for row in rows:

        technologies.append({
            "id": row[0],
            "title": row[1],
            "slug": row[2],
            "short_description": row[3],
            "description": row[4],
            "technology": row[5],
            "applications": row[6],
            "research_direction": row[7],
            "image": row[8],
            "featured": row[9],
            "created_at": row[10],
            "updated_at": row[11]
        })

    return render_template(
        "technology/index.html",
        technologies=technologies
    )


# =========================
# TECHNOLOGY DETAIL
# =========================

@technology_bp.route("/<slug>")
def technology_detail(slug):

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            id,
            title,
            slug,
            short_description,
            description,
            technology,
            applications,
            research_direction,
            image,
            featured,
            created_at,
            updated_at
        FROM technologies
        WHERE slug = %s
    """, (slug,))

    row = cur.fetchone()

    cur.close()

    if not row:
        return "Technology not found", 404

    technology = {
        "id": row[0],
        "title": row[1],
        "slug": row[2],
        "short_description": row[3],
        "description": row[4],
        "technology": row[5],
        "applications": row[6],
        "research_direction": row[7],
        "image": row[8],
        "featured": row[9],
        "created_at": row[10],
        "updated_at": row[11]
    }

    return render_template(
        "technology/detail.html",
        technology=technology
    )
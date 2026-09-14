from flask import Blueprint, render_template

from extensions import mysql

technology_bp = Blueprint(
"technology",
__name__,
url_prefix="/technology"
)

 

# TECHNOLOGY LIST

 
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
    WHERE parent_id IS NULL
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
 
 

# TECHNOLOGY DETAIL

 

@technology_bp.route("/<slug>")
def technology_detail(slug):

 cur = mysql.connection.cursor()

 
# Get main technology
 

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

 if not row:

    cur.close()

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


 
# Get child technologies
 

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
    WHERE parent_id = %s
    ORDER BY created_at ASC
""", (technology["id"],))

 child_rows = cur.fetchall()

 cur.close()


 child_technologies = []

 for child in child_rows:

    child_technologies.append({
        "id": child[0],
        "title": child[1],
        "slug": child[2],
        "short_description": child[3],
        "description": child[4],
        "technology": child[5],
        "applications": child[6],
        "research_direction": child[7],
        "image": child[8],
        "featured": child[9],
        "created_at": child[10],
        "updated_at": child[11]
    })


 return render_template(
    "technology/detail.html",
    technology=technology,
    child_technologies=child_technologies
)
 
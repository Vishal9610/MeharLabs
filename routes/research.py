from flask import Blueprint, render_template

import MySQLdb.cursors

from extensions import mysql

research_bp = Blueprint(
"research",
__name__,
url_prefix="/research"
)

 

# RESEARCH LIST

 

@research_bp.route("/")
def research_list():

  
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
        research_area,
        technology,
        status,
        image,
        featured,
        created_at,
        updated_at
    FROM research
    ORDER BY created_at DESC
""")

 research_list = cur.fetchall()

 cur.close()

 return render_template(
    "research/index.html",
    research_list=research_list
)
  

 

# RESEARCH DETAIL

 

@research_bp.route("/<slug>")
def research_detail(slug):

  
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
        research_area,
        technology,
        status,
        image,
        featured,
        created_at,
        updated_at
    FROM research
    WHERE slug = %s
""", (slug,))

 research = cur.fetchone()

 cur.close()

 if not research:
    return "Research not found", 404

 return render_template(
    "research/detail.html",
    research=research
)
  

from flask import Blueprint, render_template

import MySQLdb.cursors

from extensions import mysql

home_bp = Blueprint(
"home",
__name__
)

@home_bp.route("/")
def home():

  
  cur = mysql.connection.cursor(
    MySQLdb.cursors.DictCursor
)


 
# Featured Research
 

  cur.execute("""
    SELECT *
    FROM research
    WHERE featured = TRUE
    ORDER BY created_at DESC
    LIMIT 3
""")

  research = cur.fetchall()


 
# Featured Projects
 

  cur.execute("""
    SELECT *
    FROM projects
    WHERE featured ='Active'
    ORDER BY created_at DESC
    LIMIT 4
""")

  projects = cur.fetchall()


 
# Technologies
 

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
    LIMIT 4
""")

  technologies = cur.fetchall()


  cur.close()


  return render_template(
    "home/index.html",
    research=research,
    projects=projects,
    technologies=technologies
)
  

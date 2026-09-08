from flask import Blueprint, render_template, request
from datetime import datetime
import calendar

from extensions import mysql


analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/admin/analytics"
)


@analytics_bp.route("/")
def dashboard():

    cur = mysql.connection.cursor()

    now = datetime.now()

    # -----------------------------------
    # SELECTED MONTH
    # -----------------------------------

    selected_year = request.args.get(
        "year",
        default=now.year,
        type=int
    )

    selected_month = request.args.get(
        "month",
        default=now.month,
        type=int
    )

    # Validate month
    if selected_month < 1 or selected_month > 12:
        selected_month = now.month

    # -----------------------------------
    # SELECTED YEAR
    # -----------------------------------

    # -----------------------------------
    # SUMMARY
    # -----------------------------------

    # Total views
    cur.execute("""
        SELECT COUNT(*)
        FROM page_views
    """)

    total_views = cur.fetchone()[0]

    # Today's views
    cur.execute("""
        SELECT COUNT(*)
        FROM page_views
        WHERE view_day = %s
    """, (now.date(),))

    today_views = cur.fetchone()[0]

    # Current month views
    cur.execute("""
        SELECT COUNT(*)
        FROM page_views
        WHERE view_month = %s
        AND view_year = %s
    """, (
        now.month,
        now.year
    ))

    month_views = cur.fetchone()[0]

    # Current year views
    cur.execute("""
        SELECT COUNT(*)
        FROM page_views
        WHERE view_year = %s
    """, (now.year,))

    year_views = cur.fetchone()[0]

    # -----------------------------------
    # SELECTED MONTH ANALYTICS
    # -----------------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM page_views
        WHERE view_month = %s
        AND view_year = %s
    """, (
        selected_month,
        selected_year
    ))

    selected_month_views = cur.fetchone()[0]

    # -----------------------------------
    # SELECTED YEAR ANALYTICS
    # -----------------------------------

    cur.execute("""
        SELECT COUNT(*)
        FROM page_views
        WHERE view_year = %s
    """, (selected_year,))

    selected_year_views = cur.fetchone()[0]

    # -----------------------------------
    # PAGE ANALYTICS
    # -----------------------------------

    selected_period = request.args.get(
        "period",
        default="all"
    )

    if selected_period not in [
        "all",
        "month",
        "year"
    ]:
        selected_period = "all"

    # All Time
    if selected_period == "all":

        cur.execute("""
            SELECT
                page_name,
                page_url,
                COUNT(*) AS views
            FROM page_views
            GROUP BY page_name, page_url
            ORDER BY views DESC
        """)

    # Selected Month
    elif selected_period == "month":

        cur.execute("""
            SELECT
                page_name,
                page_url,
                COUNT(*) AS views
            FROM page_views
            WHERE view_month = %s
            AND view_year = %s
            GROUP BY page_name, page_url
            ORDER BY views DESC
        """, (
            selected_month,
            selected_year
        ))

    # Selected Year
    else:

        cur.execute("""
            SELECT
                page_name,
                page_url,
                COUNT(*) AS views
            FROM page_views
            WHERE view_year = %s
            GROUP BY page_name, page_url
            ORDER BY views DESC
        """, (selected_year,))

    page_views = cur.fetchall()

    # -----------------------------------
    # AVAILABLE YEARS
    # -----------------------------------

    cur.execute("""
        SELECT DISTINCT view_year
        FROM page_views
        ORDER BY view_year DESC
    """)

    database_years = cur.fetchall()

    years = []

    for row in database_years:
        years.append(row[0])

    # Current year always available
    if now.year not in years:
        years.insert(0, now.year)

    # Selected year always available
    if selected_year not in years:
        years.append(selected_year)

    years = sorted(
        set(years),
        reverse=True
    )

    # -----------------------------------
    # MONTHS
    # -----------------------------------

    months = []

    for month_number in range(1, 13):

        months.append({
            "number": month_number,
            "name": calendar.month_name[month_number]
        })

    # -----------------------------------
    # SELECTED MONTH NAME
    # -----------------------------------

    selected_month_name = calendar.month_name[
        selected_month
    ]

    cur.close()

    return render_template(
        "admin/analytics/index.html",

        # Summary
        total_views=total_views,
        today_views=today_views,
        month_views=month_views,
        year_views=year_views,

        # Month
        selected_month_views=selected_month_views,

        # Year
        selected_year_views=selected_year_views,

        # Page Analytics
        page_views=page_views,
        selected_period=selected_period,

        # Selectors
        years=years,
        months=months,

        selected_year=selected_year,
        selected_month=selected_month,
        selected_month_name=selected_month_name,

        current_month=calendar.month_name[now.month],
        current_year=now.year
    )
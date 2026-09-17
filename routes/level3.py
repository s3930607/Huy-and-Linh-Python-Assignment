from flask import Blueprint, render_template, request

from database import queries
from routes import choose, choose_int

bp = Blueprint("level3", __name__)

TOP_N = [5, 10, 20, 50]


@bp.route("/improvement")
def improvement():
    antigen_rows = queries.antigens()
    year_list = queries.years()

    antigen = choose(request.args.get("antigen"),
                     [row["AntigenID"] for row in antigen_rows], "MCV1")
    start_year = choose_int(request.args.get("start"), year_list, 2000)
    end_year = choose_int(request.args.get("end"), year_list, 2024)
    limit = choose_int(request.args.get("top"), TOP_N, 10)
    sort = choose(request.args.get("sort"), list(queries.IMPROVEMENT_SORT), "increase")
    direction = choose(request.args.get("dir"), ["asc", "desc"], "desc")

    # A start year after the end year would silently return nothing, which reads
    # as "no data" rather than "you asked for something impossible". Catching it
    # here lets the page say so.
    invalid_range = start_year >= end_year
    rows = [] if invalid_range else queries.biggest_improvement(
        antigen, start_year, end_year, limit, sort, direction)

    return render_template(
        "level3_improvement.html",
        antigens=antigen_rows,
        years=year_list,
        top_options=TOP_N,
        selected={"antigen": antigen, "start": start_year, "end": end_year,
                  "top": limit, "sort": sort, "dir": direction},
        invalid_range=invalid_range,
        rows=rows,
    )


@bp.route("/above-average")
def above_average():
    disease_rows = queries.diseases()
    year_list = queries.years()

    inf_type = choose(request.args.get("disease"),
                      [row["id"] for row in disease_rows], "MEA")
    year = choose_int(request.args.get("year"), year_list, 2020)
    direction = choose(request.args.get("dir"), ["asc", "desc"], "desc")

    rows = queries.above_global_average(inf_type, year, direction)

    return render_template(
        "level3_aboveavg.html",
        diseases=disease_rows,
        years=year_list,
        selected={"disease": inf_type, "year": year, "dir": direction},
        rows=rows,
        missing=queries.countries_not_reporting(inf_type, year),
    )

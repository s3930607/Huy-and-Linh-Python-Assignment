from flask import Blueprint, render_template, request

from database import queries
from routes import choose, choose_int

bp = Blueprint("level2", __name__)

THRESHOLDS = [50, 60, 70, 80, 90, 95]


@bp.route("/vaccination-rates")
def vaccination_rates():
    antigen_rows = queries.antigens()
    region_rows = queries.regions()
    country_rows = queries.countries()
    year_list = queries.years()

    antigen = choose(request.args.get("antigen"),
                     [row["AntigenID"] for row in antigen_rows], "MCV2")
    year = choose_int(request.args.get("year"), year_list, 2010)
    # "ALL" is a real option here, not a missing value, so it belongs in the
    # allowed list alongside the region and country codes.
    region = choose(request.args.get("region"),
                    [row["RegionID"] for row in region_rows] + ["ALL"], "ALL")
    country = choose(request.args.get("country"),
                     [row["CountryID"] for row in country_rows] + ["ALL"], "ALL")
    threshold = choose_int(request.args.get("threshold"), THRESHOLDS, 90)

    return render_template(
        "level2_vaccination.html",
        antigens=antigen_rows,
        regions=region_rows,
        country_options=country_rows,
        years=year_list,
        thresholds=THRESHOLDS,
        selected={"antigen": antigen, "year": year, "region": region,
                  "country": country, "threshold": threshold},
        countries=queries.countries_meeting_target(antigen, year, threshold,
                                                   region, country),
        per_region=queries.countries_met_per_region(antigen, year, threshold),
        herd=queries.herd_immunity_by_region(antigen, year, threshold),
    )


@bp.route("/infection-economy")
def infection_economy():
    disease_rows = queries.diseases()
    economy_rows = queries.economies()
    year_list = queries.years()

    inf_type = choose(request.args.get("disease"),
                      [row["id"] for row in disease_rows], "MEA")
    year = choose_int(request.args.get("year"), year_list, 2022)
    economy = choose_int(request.args.get("economy"),
                         [row["economyID"] for row in economy_rows], 4)
    sort = choose(request.args.get("sort"), list(queries.INFECTION_SORT), "rate")
    direction = choose(request.args.get("dir"), ["asc", "desc"], "desc")

    return render_template(
        "level2_infection.html",
        diseases=disease_rows,
        economies=economy_rows,
        years=year_list,
        selected={"disease": inf_type, "year": year, "economy": economy,
                  "sort": sort, "dir": direction},
        rows=queries.infections_in_economy(inf_type, year, economy, sort, direction),
        totals=queries.infection_totals_by_economy(inf_type, year),
    )

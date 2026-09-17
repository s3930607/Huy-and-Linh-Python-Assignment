from flask import Blueprint, render_template

from database import queries

bp = Blueprint("level1", __name__)


@bp.route("/")
def landing():
    return render_template(
        "level1_landing.html",
        facts=queries.headline_facts(),
        diseases=queries.diseases_with_reach(),
    )


@bp.route("/mission")
def mission():
    # Personas and the team roster are read from the database rather than written
    # into the template, because the brief requires them to be stored there.
    return render_template(
        "level1_mission.html",
        sections=queries.mission_sections(),
        personas=queries.personas(),
        team=queries.team_members(),
    )

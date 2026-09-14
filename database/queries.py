"""Every SQL statement in the project lives here.

Two rules this module exists to enforce:

1. Values chosen by the user are passed as bound parameters (the ? marks), never
   pasted into the SQL text. That is what stops a crafted input from changing the
   meaning of the query.

2. Vaccination.coverage, .doses and .target_num are declared REAL, but roughly a
   quarter of the rows store an empty string there instead. SQLite compares text
   as greater than any number, so `coverage >= 90` is true for every blank row.
   Anything that reads those three columns guards with typeof(...) = 'real'.
"""
from database.connection import run_one, run_query


#lookup lists that fill the dropdowns

def antigens():
    return run_query("SELECT AntigenID, name FROM Antigen ORDER BY AntigenID")


def diseases():
    return run_query("SELECT id, description FROM Infection_Type ORDER BY description")


def economies():
    return run_query("SELECT economyID, phase FROM Economy ORDER BY economyID")


def regions():
    return run_query("SELECT RegionID, region FROM Region ORDER BY region")


def countries():
    return run_query("SELECT CountryID, name FROM Country ORDER BY name")


def years():
    rows = run_query("SELECT YearID FROM YearDate ORDER BY YearID")
    return [row["YearID"] for row in rows]


#level 1
def headline_facts():
    return run_one("""
        SELECT (SELECT MIN(YearID) FROM YearDate)     AS first_year,
               (SELECT MAX(YearID) FROM YearDate)     AS last_year,
               (SELECT COUNT(*) FROM Country)         AS countries,
               (SELECT SUM(doses) FROM Vaccination
                 WHERE typeof(doses) = 'real')        AS total_doses,
               (SELECT SUM(cases) FROM InfectionData) AS total_cases
    """)


def diseases_with_reach():
    return run_query("""
        SELECT t.description,
               COUNT(DISTINCT i.country) AS countries_reporting
        FROM Infection_Type t
        LEFT JOIN InfectionData i ON i.inf_type = t.id
        GROUP BY t.id
        ORDER BY t.description
    """)


def mission_sections():
    return run_query("SELECT heading, body FROM MissionStatement ORDER BY display_order")


def personas():
    return run_query("""
        SELECT name, role, age, goal, frustration, tech_skill
        FROM Persona
        ORDER BY PersonaID
    """)


def team_members():
    return run_query("""
        SELECT StudentID, full_name, role, subtask
        FROM TeamMember
        ORDER BY full_name
    """)


#level 2 A: vaccination rates by country and region

def countries_meeting_target(antigen, year, threshold, region_id, country_id):
    return run_query("""
        SELECT v.antigen,
               v.year,
               c.name AS country,
               r.region,
               ROUND(v.coverage, 1) AS pct_of_target
        FROM Vaccination v
        JOIN Country c ON c.CountryID = v.country
        JOIN Region  r ON r.RegionID  = c.region
        WHERE v.antigen = ?
          AND v.year = ?
          AND typeof(v.coverage) = 'real'
          AND v.coverage >= ?
          AND (? = 'ALL' OR r.RegionID = ?)
          AND (? = 'ALL' OR c.CountryID = ?)
        ORDER BY pct_of_target DESC, c.name
    """, (antigen, year, threshold, region_id, region_id, country_id, country_id))


def countries_met_per_region(antigen, year, threshold):
    return run_query("""
        SELECT r.region,
               COUNT(DISTINCT v.country) AS countries_met,
               ROUND(AVG(v.coverage), 1) AS avg_coverage
        FROM Vaccination v
        JOIN Country c ON c.CountryID = v.country
        JOIN Region  r ON r.RegionID  = c.region
        WHERE v.antigen = ?
          AND v.year = ?
          AND typeof(v.coverage) = 'real'
          AND v.coverage >= ?
        GROUP BY r.RegionID
        ORDER BY countries_met DESC
    """, (antigen, year, threshold))


def herd_immunity_by_region(antigen, year, threshold):
    return run_query("""
        SELECT r.region,
               COUNT(DISTINCT CASE WHEN v.coverage >= ? THEN v.country END) AS met,
               COUNT(DISTINCT v.country) AS total_with_data,
               ROUND(100.0 * COUNT(DISTINCT CASE WHEN v.coverage >= ? THEN v.country END)
                     / COUNT(DISTINCT v.country), 1) AS pct_of_region
        FROM Vaccination v
        JOIN Country c ON c.CountryID = v.country
        JOIN Region  r ON r.RegionID  = c.region
        WHERE v.antigen = ?
          AND v.year = ?
          AND typeof(v.coverage) = 'real'
        GROUP BY r.RegionID
        ORDER BY pct_of_region DESC
    """, (threshold, threshold, antigen, year))


#level 2 B: infection data by economic status
INFECTION_SORT = {
    "country": "c.name",
    "rate": "cases_per_100k",
    "cases": "i.cases",
}


def order_by(choice, allowed, default, direction):
    column = allowed.get(choice, allowed[default])
    return " ORDER BY {} {}".format(column, "ASC" if direction == "asc" else "DESC")


def infections_in_economy(inf_type, year, economy_id, sort="rate", direction="desc"):
    sql = """
        SELECT t.description AS disease,
               c.name        AS country,
               e.phase       AS economic_phase,
               i.year,
               i.cases,
               ROUND(i.cases * 100000.0 / p.population, 2) AS cases_per_100k
        FROM InfectionData i
        JOIN Country           c ON c.CountryID = i.country
        JOIN Economy           e ON e.economyID = c.economy
        JOIN Infection_Type    t ON t.id        = i.inf_type
        JOIN CountryPopulation p ON p.country   = i.country AND p.year = i.year
        WHERE i.inf_type = ?
          AND i.year = ?
          AND e.economyID = ?
          AND p.population > 0
    """ + order_by(sort, INFECTION_SORT, "rate", direction)
    return run_query(sql, (inf_type, year, economy_id))


def infection_totals_by_economy(inf_type, year):
    return run_query("""
        SELECT t.description AS disease,
               e.phase,
               i.year,
               CAST(SUM(i.cases) AS INTEGER) AS total_cases,
               COUNT(DISTINCT i.country) AS countries,
               ROUND(SUM(i.cases) * 100000.0 / SUM(p.population), 2) AS cases_per_100k
        FROM InfectionData i
        JOIN Country           c ON c.CountryID = i.country
        JOIN Economy           e ON e.economyID = c.economy
        JOIN Infection_Type    t ON t.id        = i.inf_type
        JOIN CountryPopulation p ON p.country   = i.country AND p.year = i.year
        WHERE i.inf_type = ? AND i.year = ?
        GROUP BY e.economyID
        ORDER BY total_cases DESC
    """, (inf_type, year))


#level 3 A: biggest improvement in vaccination rate

IMPROVEMENT_SORT = {
    "increase": "rate_increase",
    "country": "c.name",
    "end": "end_rate",
}


def biggest_improvement(antigen, start_year, end_year, limit,
                        sort="increase", direction="desc"):
    """Countries whose vaccination rate rose most between two years.

    The brief says the rate depends on the population, so this uses
    doses / population rather than the stored coverage column.
    """
    sql = """
        WITH rate AS (
            SELECT v.country,
                   v.year,
                   v.doses * 100.0 / p.population AS vacc_rate
            FROM Vaccination v
            JOIN CountryPopulation p
              ON p.country = v.country AND p.year = v.year
            WHERE v.antigen = ?
              AND typeof(v.doses) = 'real'
              AND p.population > 0
        )
        SELECT c.name AS country,
               r.region,
               ROUND(s.vacc_rate, 2) AS start_rate,
               ROUND(e.vacc_rate, 2) AS end_rate,
               ROUND(e.vacc_rate - s.vacc_rate, 2) AS rate_increase
        FROM rate s
        JOIN rate    e ON e.country   = s.country
        JOIN Country c ON c.CountryID = s.country
        JOIN Region  r ON r.RegionID  = c.region
        WHERE s.year = ? AND e.year = ?
    """ + order_by(sort, IMPROVEMENT_SORT, "increase", direction) + " LIMIT ?"
    return run_query(sql, (antigen, start_year, end_year, limit))


#level 3 B: countries above the global infection rate

def above_global_average(inf_type, year, direction="desc"):
    """The global infection rate, then every country that exceeds it.

    Returns the global figure as the first row so the template does not have to
    stitch two result sets together.
    """
    
    sql = """
        WITH global AS (
            SELECT SUM(i.cases) * 100000.0 / SUM(p.population) AS global_rate
            FROM InfectionData i
            JOIN CountryPopulation p
              ON p.country = i.country AND p.year = i.year
            WHERE i.inf_type = ? AND i.year = ? AND p.population > 0
        )
        SELECT 0 AS sort_group,
               'Global' AS country,
               t.description AS infection_type,
               ROUND(g.global_rate, 2) AS rate_per_100k,
               ? AS year
        FROM global g
        JOIN Infection_Type t ON t.id = ?

        UNION ALL

        SELECT 1 AS sort_group,
               c.name,
               t.description,
               ROUND(i.cases * 100000.0 / p.population, 2),
               i.year
        FROM InfectionData i
        JOIN Country           c ON c.CountryID = i.country
        JOIN Infection_Type    t ON t.id        = i.inf_type
        JOIN CountryPopulation p ON p.country   = i.country AND p.year = i.year
        WHERE i.inf_type = ?
          AND i.year = ?
          AND p.population > 0
          AND i.cases * 100000.0 / p.population > (SELECT global_rate FROM global)

        ORDER BY sort_group, rate_per_100k {}
    """.format("ASC" if direction == "asc" else "DESC")
    return run_query(sql, (inf_type, year, year, inf_type, inf_type, year))


def countries_not_reporting(inf_type, year):
    """Countries with no record at all for this disease and year.

    NOT EXISTS is the natural way to ask "is there no matching row", and it lets
    the database stop looking as soon as it finds one.
    """
    return run_query("""
        SELECT c.name
        FROM Country c
        WHERE NOT EXISTS (
            SELECT 1 FROM InfectionData i
            WHERE i.country = c.CountryID
              AND i.inf_type = ?
              AND i.year = ?
        )
        ORDER BY c.name
    """, (inf_type, year))

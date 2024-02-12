import typer
from cf_u.functions import *

app = typer.Typer()

@app.command(short_help='returns the problems and links of the specified tag')
def tag(tag: str):
    get_problem_by_tag(tag)

@app.command(short_help="returns a list of 11 users, with 5 above and below of the requested user's position in the rank")
def whereis(username: str):
   get_position(username)

@app.command(short_help="returns a list of problems to practice in the range +- 200 rank of the user")
def practice(username: str):
    get_problems_to_practice(username)

@app.command(short_help="parses a contest and file setup for the problems")
def parse(contest_id: str, extension: str):
    parse_contest(contest_id, extension)

@app.command(short_help="")
def acceptance(contest_id: str):
    standings_row_extraction(contest_id)

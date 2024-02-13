import requests
from rich.console import Console
from rich.table import Table
from bs4 import BeautifulSoup
import pandas as pd

from cf_u.utilities import *

console = Console()

contest_url = "https://codeforces.com/contest/"

def get_problem_by_tag(tag: str):
    problems = []

    table = Table(show_header=True, header_style="bold purple" )
    table.add_column("Title", min_width=12, justify="left")
    table.add_column("Link", min_width=12, justify="center")

    # Iterate over problem set pages (adjust the range accordingly)
    for page_number in range(0, 2):  # You can adjust the range based on the number of pages
        problem_set_url = f'https://codeforces.com/problemset/page/{page_number}?tags={tag}'
        
        try:
            response = requests.get(problem_set_url)

            if response.status_code != 200:
                print(f"Failed to retrieve data for tag {tag}.")
                return problems

            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            console.print(f'[bold red]Error: Unable to fetch data. Try Again later or check you connection[/ bold red]')
            exit()

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')

        for row in rows:
            problem_title_tag = row.find('div', style='float: left;')
            problem_rating = row.find('span', class_='ProblemRating')

            if problem_title_tag and problem_title_tag.a:
                problem_title = problem_title_tag.a.text.strip()
                problem_link = problem_title_tag.a['href']
            else:
                problem_title = "N/A"
                problem_link = "N/A"

            if problem_title != "N/A" and problem_rating:
                problems.append({"title": problem_title, "link": problem_link, "rating": problem_rating.text})

    if not problems:
        console.print(f"[bold red]No problems found for tag {tag}[/ bold red]")
    else:
        console.print(f"Problems in the problem set related to tag {tag}:\n")
        for prob in problems:
            rating_color = get_codeforces_rating_color(int(prob['rating']));
            table.add_row(f"[{rating_color}]{prob['rating']} {prob['title']}[/{rating_color}]", f"https://codeforces.com{prob['link']}")
        console.print(table)


def get_position(username: str):
    user_data = fetch_user_data(1000)

    # Create a DataFrame from the user data
    df = pd.DataFrame(user_data, columns=['User', 'Rating', 'ProblemsSolved'])

    table = Table(show_header=True, header_style="bold blue" )
    table.add_column("Rank", min_width=12, justify="center")
    table.add_column("Username", min_width=12, justify="center")
    table.add_column("Rating", min_width=12, justify="center")
    
    # Check if the provided handle is in the DataFrame
    if username in df['User'].values:
        user_ranking = df[df['User'] == username].index[0]

        # Display users ranked 5 above and 5 below the given username's ranking
        start_rank = max(0, user_ranking - 5)
        end_rank = min(len(df), user_ranking + 6)

        users_around = df.iloc[start_rank:end_rank]
        for i, users in users_around.iterrows():
            rating_color, user_color = get_codeforces_rating_color(users['Rating']), 'grey66';
            if(users['User']==username):
                user_color = "red"
            else:
                user_color = "grey66"
            table.add_row(str(i), f"[{user_color}]{users['User']}[/{user_color}]", f"[{rating_color}]{users['Rating']}[/{rating_color}]") 
        # print(users_around)
        console.print(table)
    else:
        console.print(f"[bold red]Error: Handle '{username}' not found in the user data.[/bold red]")
        console.print(f"[bold red]I suppose you haven't participated in a contest for the past 6 months OR Try making an account[/bold red]")


def get_problems_to_practice(username: str):

    table = Table(show_header=True, header_style="bold blue" )
    table.add_column("Name", min_width=12, justify="left")
    table.add_column("Rating", min_width=12, justify="center")
    table.add_column("Link", min_width=12, justify="left")

    
    user_data = get_user_info(username)
    rank_name = user_data.get("rank", "unranked")

    current_rating = user_data.get("rating", "unrated")

    if(current_rating!="unrated"):
        rating_color = get_codeforces_rating_color(current_rating)
        console.print(f"[{rating_color}]Welcome {rank_name} {username}[/{rating_color}]")

        min_rating = current_rating
        max_rating = int(current_rating) + 200
    else :
        console.print(f"[gray66]Welcome {username}[/ gray66]")
        min_rating = 800
        max_rating = 1000
    num_problems_to_select = 200

    selected_problems = select_unsolved_problems(username, min_rating, max_rating, num_problems_to_select)

    for problem in selected_problems:
        rating_color = get_codeforces_rating_color(problem.get('rating'))
        table.add_row(f"[{rating_color}]{problem['name']}[/{rating_color}]", f"[{rating_color}]{problem.get('rating', 'unrated')}[/{rating_color}]", f"[blue]https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}[/blue]")

    console.print(table)



def parse_contest(contest_id: int, extension: str):
    contest_url = "https://codeforces.com/contest/"
    ext = ['cpp', 'py', 'java']
    if extension not in ext:
        console.print(f'[bold red]Invalid Extension![/red bold]')
        exit()

    extension = '.' + extension
    contest_url = contest_url + str(contest_id)
    print(contest_url)

    try:
        page = requests.get(contest_url, verify = True)
        if(page.status_code != 200):
            print(f"Failed to retrive contest {contest_id}")
            exit(1)
        else:
            print("Parsing...")

        page.raise_for_status()

    except requests.exceptions.RequestException as e:
        console.print(f'[bold red]Error: Unable to fetch data. Try Again later or check you connection[/ bold red]')
        exit()
    
    soup = BeautifulSoup(page.text, 'html.parser')
    contest_problem_url = f'https://codeforces.com/contest/{contest_id}'

    #Extract the contest-details
    tables = soup.findAll('table')
    contest_name = tables[0].find('a').text.strip()
    print(contest_name)

    #universal folder name
    folder_name = get_folder_name(contest_name)

    #extract the datatable 
    problems = soup.find('div', attrs={"class":"datatable"}).find('table').findAll('a')

    #create the problem folder
    os.mkdir(folder_name)

    print("Started parsing.....")

    prob_x = [] #list of problems

    for i in range(len(problems)):
        #For every contest
        if i%4 !=0 : continue
        txt = problems[i].text.strip()
        prob_no = problems[i].text.strip()
        prob_name = problems[i+1].text.strip()
        prob_x.append(prob_no)
        create_problem_folder(prob_no,prob_name,contest_problem_url,folder_name,extension,contest_id)



def standings_row_extraction(contest_id: int):
    try:
        table = Table(show_header=True, header_style="bold green" )
        table.add_column("Problem", min_width=12, justify="center")
        table.add_column("Accepted", min_width=12, justify="center")
        table.add_column("Tried", min_width=12, justify="center")
        table.add_column("Success", min_width=12, justify="center")

        page_stats = requests.get(contest_url + f'/{contest_id}' + '/standings' , verify = True)
        
        if(page_stats.status_code != 200):
            console.print(f"[bold][red]Failed to retrive stats for contest {contest_id}!!!![/red][/bold]")
            exit()

        page_stats.raise_for_status()

        soup_stats = BeautifulSoup(page_stats.text, 'html.parser')
        acc_tried = soup_stats.find('table')

        acc_tried_notice = acc_tried.findAll('span', attrs={"class": "notice"})
        acc_tried_AC = acc_tried.findAll('span', attrs={"class": "cell-passed-system-test"})
        
        x = len(acc_tried_notice)
        acc_tried_AC = acc_tried_AC[-x:] #extract last n rows
        
        for i in range(len(acc_tried_AC)):
            if i==0:continue
            
            ac_num = acc_tried_AC[i].text
            try_num = acc_tried_notice[i].text
            if int(try_num) == 0:
                per = 0
            else:
                per = (int(ac_num) / int(try_num)) * 100.00
                per = round(per,2)

            table.add_row(str(i), str(ac_num), str(try_num), f"{per}%")
        
        console.print(table)

    except requests.exceptions.RequestException as e:
        console.print(f'[bold red]Error: Unable to fetch data. Try Again later or check you connection[/ bold red]')
        exit()


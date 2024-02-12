import requests
import random
from rich.console import Console
from rich.table import Table
import random
import os
from bs4 import BeautifulSoup

console = Console()

def fetch_user_data(num_users=50):
    url = f'https://codeforces.com/api/user.ratedList?activeOnly=true'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            user_data = {
                'User': [],
                'Rating': [],
                'ProblemsSolved': []
            }

            for user in data['result']:
                user_data['User'].append(user['handle'])
                user_data['Rating'].append(user['rating'])
                user_data['ProblemsSolved'].append(user['contribution'])

            return user_data
        else:
            print(f"Error: {data['comment']}")
    else:
        print(f"Error: Unable to fetch data (HTTP status code {response.status_code})")

    return None

def get_codeforces_rating_color(rating: int) -> str:
    if rating < 1200:
        return 'grey62'
    elif rating < 1400:
        return 'green'
    elif rating < 1600:
        return 'cyan'
    elif rating < 1900:
        return 'blue'
    elif rating < 2100:
        return 'purple'
    elif rating < 2400:
        return 'orange3'
    else:
        return 'red'

def get_user_info(username):
    api_url = f'https://codeforces.com/api/user.info?handles={username}'

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        user_info = response.json()

        if user_info['status'] == 'OK':
            return user_info['result'][0]
        else:
            print(f"Error: {user_info['comment']}")

    except requests.exceptions.RequestException as e:
        console.print('[bold red]Error: Unable to connect. Try again later, or check your connection[/ bold red]')
        exit()

    return None

def get_user_solved_problems(username):
    submissions_url = f'https://codeforces.com/api/user.status?handle={username}&from=1&count=100000'
    try:
        response = requests.get(submissions_url)
        response.raise_for_status()

        submissions = response.json()['result']
        solved_problems = set()

        for submission in submissions:
            if submission['verdict'] == 'OK':
                problem = submission['problem']
                problem_id = f"{problem['contestId']}{problem['index']}"
                solved_problems.add(problem_id)

        return solved_problems

    except requests.exceptions.RequestException as e:
        print(f"Error: Try again Later")
        return set()

def get_user_current_rating(username):
    user_info = get_user_info(username)

    if user_info:
        return user_info.get('rating', 'unrated')
    else:
        return 'unrated'

def get_problems_in_rank_range(min_rank, max_rank):
    problems_url = f'https://codeforces.com/api/problemset.problems'
    try:
        response = requests.get(problems_url)
        response.raise_for_status()

        problems = response.json()['result']['problems']

        # Filter problems based on rank range
        filtered_problems = [problem for problem in problems if min_rank <= problem.get('rating', 0) <= max_rank]

        return filtered_problems

    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to connect")
        return []

def select_unsolved_problems(username, min_rank, max_rank, num_problems):
    solved_problems = get_user_solved_problems(username)
    problems_in_range = get_problems_in_rank_range(min_rank, max_rank)

    # Filter out problems the user has solved
    unsolved_problems = [problem for problem in problems_in_range if f"{problem['contestId']}{problem['index']}" not in solved_problems]

    # Select a random subset of unsolved problems
    selected_problems = random.sample(unsolved_problems, min(num_problems, len(unsolved_problems)))

    return selected_problems

# parse  ----------------------------------------------------------------------------------------------------------------
parent_path = os.getcwd()
illegal = ["<", ">", "[", "]",  "?", ":", "*" , "|"]

# Function to generate the extension of the solution file according to the language preferred by the user
def get_extension():
    language = input('\nWhat is the language of your choice? \n1-C++ \n2-C \n3-Python \n4-Java \n5-Kotlin \n6-Javascript \n7-PHP \n8-Ruby \nEnter your choice: ')
    hash = {
        1 : '.cpp',
        2 : '.c',
        3 : '.py',
        4 : '.java',
        5 : '.kt',
        6 : '.js',
        7 : '.php',
        8 : '.rb'
    }
    return hash[int(language)]

#f Extract i/o statements for the problem 
def get_contest_io(contest_problem_url,prob_folder_name,prob_no,prob_name,contest_id):
    file2 = prob_no + ".txt"
    file2 = os.path.join(prob_folder_name,file2)
    fname = open(file2, "a")
    

    url = 'https://codeforces.com/contest/{}/problem/{}'.format(contest_id,prob_no)
    page = requests.get(url, verify = True)
    soup = BeautifulSoup(page.text, 'html.parser')
    # fname.write("Problem URL: " + url)

    inp = soup.findAll('div', attrs={"class" : "input"})
    out = soup.findAll('div', attrs={"class" : "output"})

    txt = ""
    for i in range(len(inp)):
        x = inp[i].text
        y = out[i].text
        txt = txt + "\n" + x + "\n" + y

    # print(txt)
    # fname.write("\nI/O statements for {} {} \n".format(prob_no,prob_name))
    fname.write(txt)
    fname.close()    

#f Create problem folders 
def create_problem_folder(prob_no, prob_name,contest_problem_url,folder_name,extension,template_txt,contest_id):
    print(prob_no,prob_name, "\nExtracting ......")
    contest_problem_url = contest_problem_url +  prob_no
    print(contest_problem_url, "is being parsed .....")
    print(folder_name)
    
    prob_folder_name = prob_no + " " + prob_name

    for str_char in illegal:
        prob_folder_name = prob_folder_name.replace(str_char," ")
    prob_folder_name = os.path.join(folder_name, prob_folder_name)
    os.mkdir(prob_folder_name)
    print("Problem {} folder created".format(prob_no))

    file1 = prob_no + extension
    file1 = os.path.join(prob_folder_name,file1)
    fname = open(file1,"a")
    fname.write(template_txt)
    fname.close()

    print("\nGetting i/o for {} {}".format(prob_no,prob_name))
    
    get_contest_io(contest_problem_url,prob_folder_name,prob_no,prob_name,contest_id)
    print("I/O extraction Success !")

    # #create the input.txt file for personal input output
    # file3 = "input.txt"
    # file3 = os.path.join(prob_folder_name,file3)
    # fname = open(file3,"a")
    # fname.close()

    print("Done\n\n")
    # time.sleep(5)

#f Function to get the folder_name 
def get_folder_name(contest_name):
    folder_name = os.path.join(parent_path,contest_name)
    for str_char in illegal:
        folder_name = folder_name[0:10] + folder_name[10:].replace(str_char," ")
    return folder_name

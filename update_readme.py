import datetime
import os
import requests
from dateutil import relativedelta

TOKEN = os.environ["ACCESS_TOKEN"]
USERNAME = "mdanan67"
BIRTHDAY = datetime.datetime(2001, 12, 13)
HEADERS = {"Authorization": f"bearer {TOKEN}"}

ESC = "\x1b"
BOLD_WHITE = f"{ESC}[1;37m"
ORANGE = f"{ESC}[38;5;215m"
BLUE = f"{ESC}[38;5;153m"
GRAY = f"{ESC}[38;5;242m"
GREEN = f"{ESC}[32m"
RED = f"{ESC}[31m"
RESET = f"{ESC}[0m"


def get_age():
    diff = relativedelta.relativedelta(datetime.datetime.today(), BIRTHDAY)
    y = f"{diff.years} year{'s' if diff.years != 1 else ''}"
    m = f"{diff.months} month{'s' if diff.months != 1 else ''}"
    d = f"{diff.days} day{'s' if diff.days != 1 else ''}"
    cake = " 🎂" if (diff.months == 0 and diff.days == 0) else ""
    return f"{y}, {m}, {d}{cake}"


def fetch_github_stats():
    query = """
    query($login: String!) {
      user(login: $login) {
        id
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: [OWNER]) {
          totalCount
          nodes {
            stargazerCount
            nameWithOwner
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 100) {
                    totalCount
                    nodes {
                      additions
                      deletions
                      author { user { login } }
                    }
                  }
                }
              }
            }
          }
        }
        contributed: repositories(ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER]) {
          totalCount
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    res = requests.post(
        "[https://api.github.com/graphql](https://api.github.com/graphql)",
        json={"query": query, "variables": {"login": USERNAME}},
        headers=HEADERS,
    ).json()["data"]["user"]

    repos = res["repositories"]["totalCount"]
    contrib = res["contributed"]["totalCount"]
    followers = res["followers"]["totalCount"]
    commits = res["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    stars = sum(r["stargazerCount"] for r in res["repositories"]["nodes"])

    additions, deletions = 0, 0
    for r in res["repositories"]["nodes"]:
        ref = r["defaultBranchRef"]
        if ref and ref["target"]:
            for c in ref["target"]["history"]["nodes"]:
                if c["author"]["user"] and c["author"]["user"]["login"].lower() == USERNAME.lower():
                    additions += c["additions"]
                    deletions += c["deletions"]

    return repos, contrib, stars, commits, followers, additions, deletions


def line(key, val, total_width=72):
    dots_count = max(2, total_width - len(key) - len(val) - 4)
    dots = "." * dots_count
    return f"{GRAY}.{RESET} {ORANGE}{key}{RESET}: {GRAY}{dots}{RESET} {BLUE}{val}{RESET}"


def build_readme():
    repos, contrib, stars, commits, followers, add, dele = fetch_github_stats()
    net_loc = max(0, add - dele)

    repos_str = f"{repos:,}"
    contrib_str = f"{contrib:,}"
    stars_str = f"{stars:,}"
    commits_str = f"{commits:,}"
    followers_str = f"{followers:,}"
    loc_str = f"{net_loc:,}"
    add_str = f"{add:,}++"
    del_str = f"{dele:,}--"

    # Aligned bottom stats lines
    s1_left_plain = f". Repos: ....... {repos_str} {{Contributed: {contrib_str}}}"
    s1_dots = "." * max(2, 47 - len(s1_left_plain) - len(stars_str))
    stat_line_1 = (
        f"{GRAY}.{RESET} {ORANGE}Repos{RESET}: {GRAY}.......{RESET} {BLUE}{repos_str}{RESET} "
        f"{{{ORANGE}Contributed{RESET}: {BLUE}{contrib_str}{RESET}}} | "
        f"{ORANGE}Stars{RESET}: {GRAY}{s1_dots}{RESET} {BLUE}{stars_str}{RESET}"
    )

    c_dots = "." * max(2, 26 - len(commits_str))
    f_dots = "." * max(2, 22 - len(followers_str))
    stat_line_2 = (
        f"{GRAY}.{RESET} {ORANGE}Commits{RESET}: {GRAY}{c_dots}{RESET} {BLUE}{commits_str}{RESET} | "
        f"{ORANGE}Followers{RESET}: {GRAY}{f_dots}{RESET} {BLUE}{followers_str}{RESET}"
    )

    stat_line_3 = (
        f"{GRAY}.{RESET} {ORANGE}Lines of Code on GitHub{RESET}: {GRAY}...{RESET} "
        f"{BLUE}{loc_str}{RESET} ( {GREEN}{add_str}{RESET}, {RED}{del_str}{RESET} )"
    )

    content = "\n".join([
        "```ansi",
        f"{BOLD_WHITE}atif@mostoba{RESET} {GRAY}{'-' * 60}{RESET}",
        line("OS", "Windows 11, Linux (Ubuntu)"),
        line("Uptime", get_age()),
        line("Host", "Full-Stack Developer"),
        line("Kernel", "3mtechbd.com (Backend Dev)"),
        line("IDE", "VS Code, Visual Studio"),
        f"{GRAY}.{RESET}",
        line("Languages.Programming", "C#, TypeScript, JavaScript (ES6), Python"),
        line("Frameworks.Stack", "ASP.NET Core, Blazor, Node.js, Next.js, Express.js"),
        line("Databases.And.Infra", "PostgreSQL, MongoDB, MySQL, Redis, Docker, Nginx"),
        line("Languages.Real", "English, Bengali"),
        line("Focus.Architecture", "Clean Arch, Microservices, MCP Servers"),
        line("Education", "BSc in CSE (IUBAT - 2026)"),
        f"{GRAY}.{RESET}",
        f"{BOLD_WHITE}- Contact{RESET} {GRAY}{'-' * 63}{RESET}",
        line("Email.Personal", "atifmostoba456@gmail.com"),
        line("LinkedIn", "mdanan67"),
        line("StackOverflow", "22302214"),
        line("Socials.X.Reddit", "mdanan67"),
        line("Phone", "+8801935579051"),
        f"{GRAY}.{RESET}",
        f"{BOLD_WHITE}- GitHub Stats{RESET} {GRAY}{'-' * 58}{RESET}",
        stat_line_1,
        stat_line_2,
        stat_line_3,
        "```",
        "",
    ])

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    build_readme()

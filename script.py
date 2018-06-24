 # -*- coding: utf-8 -*-
import os
import re
import requests
from bs4 import BeautifulSoup as bs

to_do = [
("http://peerproduction.net/issues/issue-0/peer-reviewed-papers/sociology-of-critique/", False),
("http://peerproduction.net/issues/issue-0/debate-ant-and-power/domination-networks/", False),
("http://peerproduction.net/issues/issue-1/invited-comments/beyond-digital-plenty/", False),
("http://peerproduction.net/issues/issue-1/invited-comments/changing-the-system-of-production/", False),
("http://peerproduction.net/issues/issue-1/debate-societal-transformation/a-note-on-evaluation-processes-for-social-phenomena-with-ambitious-claims/", False),
("http://peerproduction.net/issues/issue-3-free-software-epistemics/peer-reviewed-papers/free-software-trajectories-from-organized-publics-to-formal-social-enterprises/", False),
("http://peerproduction.net/issues/issue-3-free-software-epistemics/debate/there-is-no-free-software/", True),
("http://peerproduction.net/issues/issue-3-free-software-epistemics/debate/desired-becomings/", True),
("http://peerproduction.net/issues/issue-4-value-and-currency/invited-comments/between-copyleft-and-copyfarleft-advance-reciprocity-for-the-commons/", False),
("http://peerproduction.net/issues/issue-5-shared-machine-shops/peer-reviewed-articles/feminist-hackerspaces-the-synthesis-of-feminist-and-hacker-cultures/", False),
("http://peerproduction.net/issues/issue-6-disruption-and-the-law/peer-reviewed-articles/peer-to-peer-as-a-design-principle-for-law-distribute-the-law/", True),
("http://peerproduction.net/issues/issue-7-policies-for-the-commons/peer-reviewed-papers/policy-for-a-social-economy/", False),
("http://peerproduction.net/issues/issue-7-policies-for-the-commons/peer-reviewed-papers/towards-a-new-reconfiguration-among-the-state-civil-society-and-the-market/", False),
("http://peerproduction.net/issues/issue-8-feminism-and-unhacking-2/feminist-hackingmaking-exploring-new-gender-horizons-of-possibility/", True),
("http://peerproduction.net/issues/issue-9-alternative-internets/peer-reviewed-papers/in-defense-of-the-digital-craftsperson/", False),
("http://peerproduction.net/issues/issue-9-alternative-internets/editorial-notes/", True),
("http://peerproduction.net/issues/issue-9-alternative-internets/peer-reviewed-papers/finding-an-alternate-route-towards-open-eco-cyclical-and-distributed-production/", False),
("http://peerproduction.net/issues/issue-9-alternative-internets/experimental-format/alternative-policies-for-alternative-internets/", False),
("http://peerproduction.net/issues/issue-10-peer-production-and-work/now-the-commons/", True),
("http://peerproduction.net/issues/issue-11-city/experimental-format/singular-technologies-the-third-technoscape/", False)
]

author = ""
title = ""

def main():

    for stuff in to_do:
        url, full_two_columns = stuff
        make_html_for_pandoc(url, full_two_columns)
        convert_html_to_tex()
        pdflatex(url.split('/')[-2])

def make_html_for_pandoc(url, full_two_columns=False):

    global author, title

    # Get html
    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = bs(r.text, "lxml")
    elem = soup.find("div", {"class": lambda x: x and "main" in x})

    # Remove useless stuff
    classes_to_delete = ["breadcrumb", "pr-box-rating-articlepage", "pr-box-download"]
    for c in classes_to_delete:
        e = elem.find("div", {"class": lambda x: x and c in x})
        if e:
            e.decompose()

    # Parse author
    e = elem.find(text=re.compile("^[bB]y"))
    if e:
        author = e.parent.get_text()
        e.parent.decompose()

    # Parse title
    title = str(elem.find("span", {"class": lambda x: x and "title" in x}).text).strip()
    elem.find("span", {"class": lambda x: x and "title" in x}).decompose()


    e = elem.find('h1')
    if e:
        e.decompose()

    # Add start of two columns
    if not full_two_columns:
        e = elem.find('h2')
        if e:
            e.insert_before("STARTMULTICOLS\n")
        elem = str(elem)
    else:
        elem = "STARTMULTICOLS\n" + str(elem)

    open("tmp.html", "w").write("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
</head>
<body>
%%BODY%%
</body>
</html>
""".replace("%%BODY%%", elem))




def convert_html_to_tex():
    headers = """
\\documentclass[10pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage{lmodern, alltt, color, geometry, multicol, eurosym, fancyhdr}
\\usepackage[hyperindex=true, colorlinks=true, urlcolor=black, linkcolor=black, breaklinks=true]{hyperref}
\\renewcommand*{\\familydefault}{\\sfdefault}
\\pagestyle{empty}
\\geometry{hmargin=1cm, vmargin=2cm}
\\headsep 10pt
\\setcounter{secnumdepth}{0}
\\addtolength{\\parskip}{6pt}
\\renewcommand{\\ttdefault}{pcr}
\setlength{\\parindent}{0cm}
\pagestyle{fancy}
\\fancyhead{}
\\lfoot{}
\\cfoot{\\thepage{}}
\\rfoot{}
\\makeatletter
\\makeatother

\\title{%%TITLE%%}
\\author{%%AUTHOR%%}
\\date{}

\\begin{document}

\\maketitle

\\begin{center}
\\noindent\\rule{8cm}{0.4pt}
\\end{center}
"""
    headers = headers.replace("%%TITLE%%", title).replace("%%AUTHOR%%", author)

    closing = """
\\end{multicols}
\\end{document}
"""

    open("tmp.tex","w").write(headers)
    os.system("pandoc tmp.html -f html -t latex | sed 's/STARTMULTICOLS/\\\\begin{multicols}{2}/g' >> tmp.tex")
    open("tmp.tex", "a").write(closing)


def pdflatex(name):

    os.system("rm tmp.pdf")
    os.system("mkdir -p output")
    os.system("pdflatex -interaction nonstopmode tmp.tex")
    os.system("cp tmp.pdf output/%s.pdf" % name)

main()

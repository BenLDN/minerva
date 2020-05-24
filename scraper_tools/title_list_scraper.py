import requests
from bs4 import BeautifulSoup
from collections import OrderedDict


def get_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    return BeautifulSoup(page.content, 'html.parser')


def search_title_elements(content, rules):
    titles = []

    for rule in rules:
        if rule[0] == 0:
            titles += content.find_all(attrs=rule[1])
        elif rule[1] == 0:
            titles += content.find_all(rule[0])
        else:
            titles += content.find_all(rule[0], attrs=rule[1])

    return titles


def elements_to_list(title_elements):
    title_list = []

    for title in title_elements:
        title_list.append(title.text)

    clean_list = [s.strip().replace('\n', ' ') for s in title_list]
    deduped_list = list(OrderedDict.fromkeys(clean_list))
    return deduped_list


def get_title_list_from_site(site):
    content = get_content(site['link'])
    title_elements = search_title_elements(content, site['rules'])
    return elements_to_list(title_elements)

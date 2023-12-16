#!/usr/bin/python3

"""
dwd.py: DigitalWhisper Downloader. Bulk download sheets from digitalwhisper.co.il.
author: romansko
usage: python dwd.py <latest_sheet>
"""

import os
import sys
import requests
import re
from bs4 import BeautifulSoup


def get_sheets():
    print(f"[*] Downloading DigitalWhisper sheets..")
    issue_number = 0
    notFoundCount = 0
    while True:
        latest = issue_number - notFoundCount + 1 # +1 because first issue is Issue1. Not 0.
        if notFoundCount == 3:   # Need to know when to quit..
            print(f'[!] Assuming latest {notFoundCount} sheets are yet to be published. Halting sheets search.') 
            return latest
        try:
            issue_number += 1
            fname = f'DigitalWhisper{issue_number:03}.pdf'
            if os.path.isfile(fname):
                print(f'[*] {fname} already exists. Skipping..')
                continue
            url = f'https://www.digitalwhisper.co.il/files/Zines/0x{issue_number:02X}/DigitalWhisper{issue_number}.pdf'
            r = requests.get(url, allow_redirects=True)
            if r:
                notFoundCount = 0
                open(fname, 'wb').write(r.content)
                print(f'[*] Written {fname}.{" "*20}')
            else:
                notFoundCount += 1
                print(f'[!] {fname} Not found.')
        except Exception as e:
            print(f'[!] {e}')
            return latest
  

def get_content_old():
    """ digitalwhisper.co.il/Issues is not frequently updated. """
    try:
        fname = 'Content.html'
        r = requests.get('https://www.digitalwhisper.co.il/Issues', allow_redirects=False)
        content = r.text
        content = re.sub(r'../../issue([0-9])([^0-9])', r'DigitalWhisper00\1.pdf\2', content)      # single digit match
        content = re.sub(r'../../issue([0-9]{2})([^0-9])', r'DigitalWhisper0\1.pdf\2', content)    # 2 digits match
        content = re.sub(r'../../issue([0-9]{3})', r'DigitalWhisper\1.pdf', content)               # 3 digits match    
        
        soup = BeautifulSoup(content, 'html.parser')
        for div in soup.find_all("div", {'class':'navi'}):   # remove navigation panel
            div.decompose()
        for div in soup.find_all("img"):   # remove img links
            div.decompose()
        
        border = "<h3><center>עמוד הגליונות</center></h3>"
        content = re.sub(rf'{border}.*', '', str(soup), flags=re.DOTALL).strip()
        
        with open(fname, "w", encoding=r.encoding) as f:
            f.write(content)
            print('')
            print(f'Written {fname}.') 
    except Exception as e:
        print(f'[!] {e}')


def try_remove_stuff(div):
    stuff = ['Adobe Reader', 'Foxit Reader']
    try:
        for styler in div.find_all('div', style=re.compile("background-color")):
            styler['style'] = ''
        for styler in div.find_all('span', style=re.compile("font-size")):
            styler['style'] = ''
        for font in div.find_all('font'):
            font['size'] = ''
        for link in div.find_all('a', href=re.compile('../../files/Zines')):
            link['href'] = link['href'].replace('../../files/Zines', 'https://www.digitalwhisper.co.il/files/Zines')
            link['target'] = '_blank'
        for thing in stuff:
            div_to_remove = div.find(string=thing).find_parent()
            if div_to_remove.name == 'a':
                div_to_remove = div_to_remove.find_parent()
            div_to_remove.extract()
        for h in div.find_all('h2'):
            h.extract()  # no need for headers.
        return div
    except Exception as e:
        print(f'[!] {e}')
        return div  # return the original div


def get_content_lemma(issue_number):
    try:
        url = f'https://www.digitalwhisper.co.il/Issue{issue_number}'
        r = requests.get(url, allow_redirects=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        content = soup.find('div', id='content')
        if content:
            content = try_remove_stuff(content)
            for link in content.find_all('a', href=re.compile(r'https://www.digitalwhisper.co.il/files/Zines/.*DigitalWhisper.*\.pdf')):
                link['href'] = 'DigitalWhisper{:03}.pdf'.format(issue_number)
            return content
        return ''
    except Exception as e:
        print(f'[!] {e}')
        return ''


def get_content(latest):
    """ very slow. consider parrallelizing. """
    try:
        fname = 'Content.html'
        with open(fname, "w", encoding='UTF-8') as f:
            f.write('<html>\n<body>\n')
            for issue_number in range(1, latest):
                print(f"[*] Writing Issue {issue_number}'s brief..")
                soup = BeautifulSoup(str(get_content_lemma(issue_number)), 'html.parser')
                f.write(soup.prettify())
            f.write('\n<\\body>\n<\\html>')
        print(f'[*] Written issues brief within {fname}.') 
    except Exception as e:
        print(f'[!] {e}')


if __name__ == "__main__":
    latest = get_sheets()
    get_content(latest)

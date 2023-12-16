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
    print(f"Downloading DigitalWhisper sheets..")
    issue_number = 0
    notFoundCount = 0
    newline = ''
    while True:
        latest = issue_number - notFoundCount
        if notFoundCount == 3:   # Need to know when to quit..
            print(f'Assuming latest {notFoundCount} sheets are yet to be published. Halting sheets search.') 
            return latest
        try:
            issue_number += 1
            fname = f'DigitalWhisper{issue_number:03}.pdf'
            if os.path.isfile(fname):
                print(f'\r{fname} already exists. Skipping..', end='')
                newline = '\n'
                continue
            url = f'https://www.digitalwhisper.co.il/files/Zines/0x{issue_number:02X}/DigitalWhisper{issue_number}.pdf'
            r = requests.get(url, allow_redirects=True)
            if r:
                notFoundCount = 0
                open(fname, 'wb').write(r.content)
                print(f'\rWritten {fname}.{" "*20}', end='')
                newline = '\n'
            else:
                notFoundCount += 1
                print(f'{newline}{fname} Not found. Try WaybackMachine (web.archive.org) if {fname} was published.')
                newline=''
        except Exception as e:
            print(e)
            return latest
  

def get_content_old():
    """ digitalwhisper.co.il/Issues is not frequently updated. """
    try:
        fname = 'Content.html'
        r = requests.get('https://www.digitalwhisper.co.il/Issues', allow_redirects=True)
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
        print(e)


def get_content_lemma(issue_number):
    try:
        print(f'\rGetting content for issue {issue_number}..', end='')
        r = requests.get(f'https://www.digitalwhisper.co.il/issue{issue_number}', allow_redirects=False)
        content = r.text
        
        soup = BeautifulSoup(content, 'html.parser')
        for div in soup.find_all("div", {'class':'navi'}):   # remove navigation panel
            div.decompose()
        for div in soup.find_all("img"):   # remove img links
            div.decompose()
        
        start = "<h2><center>הגיליון"
        content = re.sub(rf'{start}.*', '', str(soup), flags=re.DOTALL).strip()
        
        end = "<hr"
        content = re.sub(rf'{end}.*', '', str(soup), flags=re.DOTALL).strip()

        return content
    except Exception as e:
        print(e)
        return ''


def get_content(latest):
    """ very slow. consider parrallelizing. """
    try:
        fname = 'Content.html'
        content = ''
        for issue_number in range(1, latest):
            content += get_content_lemma(issue_number)
        with open(fname, "w", encoding='UTF-8') as f:
            f.write(content)
            print('')
            print(f'Written {fname}.') 
    except Exception as e:
        print(e)


if __name__ == "__main__":
    latest = get_sheets()
    #get_content(latest)
    get_content_old()

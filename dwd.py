#!/usr/bin/env python

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

def getSheets(latest):
    print(f"Downloading DigitalWhisper 1:{latest}..")
    notFoundCount = 0
    for i in range(1, latest + 1):
        if notFoundCount == 3:   # Need to know when to quit..
            print(f'Assuming latest {notFoundCount} sheets are yet to be published. Halting sheets search..') 
            return
        try:
            fname = f'DigitalWhisper{i:03}.pdf'
            if os.path.isfile(fname):
                print(f'{fname} already exists. Skipping..')
                continue
            url = f'https://www.digitalwhisper.co.il/files/Zines/0x{i:02X}/DigitalWhisper{i}.pdf'
            r = requests.get(url, allow_redirects=True)
            if r:
                notFoundCount = 0
                open(fname, 'wb').write(r.content)
                print(f'Written {fname}')
            else:
                notFoundCount += 1
                print(f'{fname} Not found. Try searching with WaybackMachine (web-old.archive.org).')
                
        except Exception as e:
            print(e)
    

def getContent():
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


if __name__ == "__main__":
    try:
        latest = int(sys.argv[1])
    except: 
        latest = 0xFF
    getSheets(latest)

    # sheets summary
    getContent()

import re
import time
import csv
import sys
import argparse
import random
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup


class LinkedInScraper:
    def __init__(self, li_at_cookie, delay_range=(2, 5)):
        
        self.li_at_cookie = li_at_cookie
        self.delay_range = delay_range
        self.session = self._create_session()
        
    def _create_session(self):
        session = requests.Session()
        
        session.cookies.set('li_at', self.li_at_cookie, domain='.linkedin.com')
        session.cookies.set('JSESSIONID', 'ajax:' + str(random.randint(1000000000000, 9999999999999)), domain='.linkedin.com')
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        return session
    
    def scrape_urls(self, urls):
        results = []
        total = len(urls)
        
        for idx, url in enumerate(urls, 1):
            print(f"[{idx}/{total}] Processing: {url}")
            
            result = self._scrape_single_url(url)
            if result:
                results.append(result)
                print(f"Found URN: {result['urn']}")
            else:
                print(f"Failed")
            
            if idx < total:
                delay = random.uniform(*self.delay_range)
                print(f"  Waiting {delay:.1f}s...")
                time.sleep(delay)
        
        return results
    
    def _scrape_single_url(self, url):
        try:
            response = self.session.get(url, timeout=20, allow_redirects=True)
            
            if response.status_code == 999:
                print(f" :( Rate limited (999)")
                return None
            
            if response.status_code != 200:
                print(f" :( HTTP {response.status_code}")
                return None
            
            html = response.text
            
            if 'authwall' in html.lower() or 'login' in response.url:
                print(f" :( Auth wall - Invalid cookie")
                return None
            
            if '/company/' in url:
                return self._extract_company_data(html, url)
            elif '/in/' in url:
                return self._extract_person_data(html, url)
            else:
                print(f" :( Unknown URL type")
                return None
            
        except requests.exceptions.Timeout:
            print(f" :( Timeout")
            return None
        except Exception as e:
            print(f" :( Error: {str(e)}")
            return None
    
    def _extract_company_data(self, html, url):
        
        urn_match = re.search(r'urn:li:fsd_company:(\d+)', html)
        if not urn_match:
            print(f" :( No company URN found")
            return None
        
        urn = urn_match.group(0)
        entity_id = urn_match.group(1)
        
        return {
            'input_url': url,
            'entity_type': 'company',
            'urn': urn,
            'entity_id': entity_id,
        }
    
    def _extract_person_data(self, html, url):        
        urn_match = re.search(r'urn:li:fsd_profile:([\w-]+)', html)
        if not urn_match:
            urn_match = re.search(r'urn:li:member:(\d+)', html)
            if not urn_match:
                print(f" :( No person URN found")
                return None
        
        urn = urn_match.group(0)
        entity_id = urn_match.group(1)
                
        return {
            'input_url': url,
            'entity_type': 'person',
            'urn': urn,
            'entity_id': entity_id
        }
        
    def save_to_csv(self, results, output_file):
        if not results:
            print("\nNo results")
            return
        
        fieldnames = ['input_url', 'entity_type', 'urn', 'entity_id']
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
    
  

def read_urls_from_file(filepath):
    urls = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    except FileNotFoundError:
        print(f" :( File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR reading file: {e}")
        sys.exit(1)
    
    return urls



def main():
    parser = argparse.ArgumentParser(
        description='LinkedIn URN Scraper - Companies and People',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('url', nargs='?', help='Single LinkedIn URL (company or person)')
    parser.add_argument('-i', '--input', help='Input file with URLs (one per line)')
    parser.add_argument('-o', '--output', default='output/output.csv', help='Output CSV file (default: output.csv)')
    parser.add_argument('-c', '--cookie', help='LinkedIn li_at cookie value')
    parser.add_argument('--cookie-file', help='File containing li_at cookie')
    parser.add_argument('--delay-min', type=float, default=2.0, help='Minimum delay (default: 2s)')
    parser.add_argument('--delay-max', type=float, default=5.0, help='Maximum delay (default: 5s)')
    parser.add_argument('--help-cookie', action='store_true', help='Show cookie instructions')
    
    args = parser.parse_args()
    
    if args.help_cookie:
        sys.exit(0)
    
    cookie = None
    if args.cookie:
        cookie = args.cookie
    elif args.cookie_file:
        try:
            with open(args.cookie_file, 'r') as f:
                cookie = f.read().strip()
        except Exception as e:
            print(f"ERROR reading cookie file: {e}")
            sys.exit(1)
    else:
        print("ERROR: LinkedIn cookie required!")
        print("\nUse --help-cookie to check for problems")
        sys.exit(1)
    
    urls = []
    if args.url:
        urls = [args.url]
    elif args.input:
        urls = read_urls_from_file(args.input)
    else:
        parser.print_help()
        sys.exit(1)
    
    if not urls:
        print(" :( No URLs to process")
        sys.exit(1)
    
    scraper = LinkedInScraper(
        li_at_cookie=cookie,
        delay_range=(args.delay_min, args.delay_max)
    )
    
    results = scraper.scrape_urls(urls)
    scraper.save_to_csv(results, args.output)
    
    print(f"-----Success-----")


if __name__ == '__main__':
    main()
#!/usr/bin/env python
"""
Import meets and problems from Calculum website (https://calculum.aediroum.ca/)
and their associated Kattis contests into the local database.
"""
import os
import sys
import django
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
import string

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from board.models import Meet, Problem, Session
from django.contrib.auth.models import User


def fetch_calculum_posts():
    """Fetch all posts from the main Calculum page"""
    url = "https://calculum.aediroum.ca/"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        posts = []
        # Find all post list items
        for li in soup.find_all('li'):
            link = li.find('a')
            if link and '/posts/' in link.get('href', ''):
                post_url = urljoin(url, link['href'])
                article = link.find('article')
                if article:
                    header = article.find('header')
                    if header:
                        h3 = header.find('h3')
                        time_elem = header.find('time')
                        # Get description from <p> tag after the header
                        description = ''
                        p_tag = article.find('p')
                        if p_tag:
                            description = p_tag.get_text(strip=True)
                        
                        if h3 and time_elem:
                            # Get title from span inside h3
                            span = h3.find('span')
                            if span:
                                title = span.get_text(strip=True)
                            else:
                                title = h3.get_text(strip=True)
                            datetime_str = time_elem.get('datetime', '')
                            posts.append({
                                'url': post_url,
                                'title': title,
                                'datetime': datetime_str,
                                'description': description
                            })
        
        return posts
    except Exception as e:
        print(f"Failed to fetch posts: {str(e)}")
        return []


def generate_random_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


def get_or_create_manager(full_name):
    """Get or create a User based on full name"""
    if not full_name or full_name.strip() == '':
        return None
    
    # Split full name into first and last name
    name_parts = full_name.strip().split()
    if len(name_parts) == 0:
        return None
    elif len(name_parts) == 1:
        first_name = name_parts[0]
        last_name = ''
    else:
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:])
    
    # Normalize for username (lowercase, no accents, firstname_lastname)
    import unicodedata
    
    def normalize_name(name):
        nfkd_form = unicodedata.normalize('NFKD', name.lower().strip())
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    normalized_first = normalize_name(first_name)
    normalized_last = normalize_name(last_name)
    
    # Create username: firstname_lastname
    if normalized_last:
        username = f"{normalized_first}_{normalized_last}"
    else:
        username = normalized_first
    
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'password': generate_random_password()
            }
        )
        return user
    except Exception as e:
        print(f"      ⚠ Warning: Could not create user '{full_name}': {str(e)}")
        return None


def parse_managers(author_text):
    """Parse manager names from author text, splitting by 'et' for multiple names"""
    if not author_text or author_text.strip() == '':
        return []
    
    # Split by ' et ' to handle multiple managers
    import re
    names = re.split(r'\s+et\s+', author_text.strip(), flags=re.IGNORECASE)
    
    managers = []
    for name in names:
        name = name.strip()
        if name:
            manager = get_or_create_manager(name)
            if manager:
                managers.append(manager)
    
    return managers


def create_algo_file(meet_date):
    """Create a placeholder algo file for the meet"""
    year = meet_date.year
    month = meet_date.month
    day = meet_date.day
    
    algo_dir = os.path.join(
        os.path.dirname(__file__),
        'board',
        'meets',
        str(year),
        f"{month:02d}"
    )
    
    os.makedirs(algo_dir, exist_ok=True)
    
    algo_file = os.path.join(algo_dir, f"{day:02d}.py")
    if not os.path.exists(algo_file):
        with open(algo_file, 'w', encoding='utf-8') as f:
            f.write("# Algorithms for this session\n")
            f.write(f"# Date: {meet_date.strftime('%Y-%m-%d')}\n\n")


def process_individual_problems(soup, meet):
    """Extract individual problem links from page content"""
    problems_count = 0
    problems_seen = set()
    
    # Find all links in the page
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        
        # Check for Kattis individual problem links
        if 'kattis.com/problems/' in href:
            if href not in problems_seen:
                problems_seen.add(href)
                try:
                    problem, created = Problem.objects.get_or_create(
                        link=href,
                        defaults={
                            'platform': 'Kattis'
                        }
                    )
                    problem.meets.add(meet)
                    if created:
                        problems_count += 1
                except Exception as e:
                    pass  # Silently skip errors
        
        # Check for LeetCode problem links
        elif 'leetcode.com/problems/' in href:
            if href not in problems_seen:
                problems_seen.add(href)
                try:
                    problem, created = Problem.objects.get_or_create(
                        link=href,
                        defaults={
                            'platform': 'LeetCode'
                        }
                    )
                    problem.meets.add(meet)
                    if created:
                        problems_count += 1
                except Exception as e:
                    pass  # Silently skip errors
    
    return problems_count


def process_kattis_contest(kattis_url, meet):
    """Fetch problems from a Kattis contest"""
    problems_count = 0
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(kattis_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables - the problems table is usually the second one
        tables = soup.find_all('table')
        if len(tables) < 2:
            print("    ⚠ No problems table found on Kattis page")
            return 0
        
        problems_table = tables[1]
        
        # Extract problems from table rows
        problems_seen = set()  # Track to avoid duplicates
        for tr in problems_table.find_all('tr')[1:]:  # Skip header
            tds = tr.find_all('td')
            if len(tds) >= 2:
                # Find the problem link in the row
                for td in tds:
                    link = td.find('a')
                    if link and link.get('href'):
                        problem_path = link.get('href')
                        if '/problems/' in problem_path or '/contest' in problem_path:
                            problem_url = urljoin(kattis_url, problem_path)
                            
                            # Avoid processing the same URL twice
                            if problem_url in problems_seen:
                                continue
                            problems_seen.add(problem_url)
                            
                            # Create Problem if it doesn't exist
                            try:
                                problem, created = Problem.objects.get_or_create(
                                    link=problem_url,
                                    defaults={
                                        'platform': 'Kattis'
                                    }
                                )
                                problem.meets.add(meet)
                                
                                if created:
                                    problems_count += 1
                            except Exception as e:
                                print(f"      ✗ Error creating problem {problem_url}: {str(e)}")
                            break  # Move to next row after finding the first link
        
        return problems_count
        
    except Exception as e:
        print(f"    ✗ Error fetching Kattis contest: {str(e)}")
        return 0


def process_post(post):
    """Process a single post and extract Kattis/LeetCode links"""
    post_url = post['url']
    raw_title = post['title']
    datetime_str = post['datetime']
    description = post.get('description', '')
    
    # Skip only presentation posts
    if 'présentation' in raw_title.lower():
        print(f"  ⊘ Skipping: {raw_title} (presentation only)")
        return 'skipped'
    
    try:
        # Extract clean title: remove "Rencontre #X:" or "Concours #X:" prefix
        import re
        title = re.sub(r'^(?:Rencontre|Concours)\s*#\d+:\s*', '', raw_title, flags=re.IGNORECASE).strip()
        
        # Parse the datetime
        try:
            meet_date = datetime.fromisoformat(datetime_str).date()
        except:
            print(f"  ⊘ Skipping: {raw_title} (invalid date: {datetime_str})")
            return 'skipped'
        
        # Create algo file first (before creating/getting the meet)
        try:
            create_algo_file(meet_date)
        except Exception as e:
            print(f"  ⚠ Warning: Could not create algo file for {raw_title}: {str(e)}")
        
        # Fetch the post page
        response = requests.get(post_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract manager names from <address> tag
        managers_list = []
        address_tag = soup.find('address')
        if address_tag:
            address_text = address_tag.get_text(strip=True)
            # Extract names from "par Name" or "par Name et Name" format
            if address_text.startswith('par '):
                author_names = address_text[4:].strip()
                managers_list = parse_managers(author_names)
        
        # Find Kattis contest link first
        kattis_contest_url = None
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'kattis.com/contests' in href:
                kattis_contest_url = href
                break
        
        # Create or get the Meet
        meet, created = Meet.objects.get_or_create(
            date=meet_date,
            defaults={
                'theme': title,
                'description': description,
                'contest_link': kattis_contest_url or '',
                'get_problems': bool(kattis_contest_url)
            }
        )
        
        # Update description and contest_link if meet already exists
        if not created:
            if meet.description != description:
                meet.description = description
            if meet.contest_link != (kattis_contest_url or ''):
                meet.contest_link = kattis_contest_url or ''
                meet.get_problems = bool(kattis_contest_url)
            meet.save()
        
        # Add managers to the meet
        if managers_list:
            for manager in managers_list:
                meet.managers.add(manager)
        
        if created:
            print(f"  ✓ Created Meet: {title} ({meet_date})")
            if managers_list:
                for manager in managers_list:
                    print(f"    └─ Manager: {manager.first_name} {manager.last_name}")
        else:
            print(f"  → Updating Meet: {title} ({meet_date})")
            if managers_list:
                for manager in managers_list:
                    print(f"    └─ Manager: {manager.first_name} {manager.last_name}")
        
        # Process problems: only look for individual links if there's no contest link
        problems_count = 0
        
        if not kattis_contest_url:
            # Only process individual problem links if no contest link exists
            # (contest problems will be fetched automatically by Meet.save() via _fetch_kattis_problems)
            problems_count = process_individual_problems(soup, meet)
        
        if problems_count > 0 or created:
            if problems_count > 0:
                print(f"    └─ {problems_count} problems imported/updated")
            return 'imported'
        else:
            return 'skipped'
        
    except Exception as e:
        print(f"  ✗ Error processing {raw_title}: {str(e)}")
        return 'skipped'


def main():
    print("🔄 Starting import of Calculum meets and problems...")
    
    try:
        # Fetch all posts from Calculum
        posts = fetch_calculum_posts()
        print(f"📋 Found {len(posts)} posts on Calculum\n")
        
        imported_count = 0
        skipped_count = 0
        
        for post in posts:
            result = process_post(post)
            if result == 'imported':
                imported_count += 1
            elif result == 'skipped':
                skipped_count += 1
        
        print(f"\n✅ Import complete!")
        print(f"  Imported: {imported_count}")
        print(f"  Skipped: {skipped_count}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

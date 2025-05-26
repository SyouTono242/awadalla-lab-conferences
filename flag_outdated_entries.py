#!/usr/bin/env python3

import re
from datetime import datetime
from dateutil import parser as dateparser

def extract_name_and_url(text):
    """Extract display name and URL from markdown [text](url) syntax."""
    match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', text)
    if match:
        return match.group(1), match.group(2)
    else:
        return text, None  # no URL

def extract_tables(md_text):
    """Extracts tables and their headers from markdown text."""
    tables = []
    blocks = md_text.split('\n\n')
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) >= 3 and lines[1].startswith('|'):
            tables.append(lines)
    return tables

def parse_markdown_table(table_lines):
    """Parses markdown table lines into a list of dictionaries."""
    headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
    rows = []
    for line in table_lines[2:]:  # skip header and separator
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) == len(headers):
            row = dict(zip(headers, cells))
            rows.append(row)
    return rows

def contains_outdated_date(date_str, today):
    """Returns True if the date is in the past."""
    try:
        parsed_date = dateparser.parse(date_str, fuzzy=True, dayfirst=False)
        return parsed_date.date() < today
    except Exception:
        return False

def extract_years_from_url(url):
    """Finds all 4-digit numbers in the URL that look like years."""
    return [int(y) for y in re.findall(r'(20\d{2})', url)]

def check_outdated_entries(rows, today, current_year):
    """Returns outdated date rows and URLs with outdated years."""
    outdated_dates = []
    outdated_urls = []

    for row in rows:
        raw_name = row.get('Conference', '[Unnamed]')
        name, url = extract_name_and_url(raw_name)

        # Check dates
        for key in ['StartDate', 'EndDate']:
            if key in row and contains_outdated_date(row[key], today):
                outdated_dates.append((name, key, row[key]))
                break

        # Check URLs for outdated years
        if url:
            years_in_url = extract_years_from_url(url)

            for year in years_in_url:
                if year < current_year:
                    outdated_urls.append((name, url, year))
                    break

    return outdated_dates, outdated_urls


def main():
    with open("./README.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    today = datetime.today().date()
    current_year = today.year
    tables = extract_tables(md_text)

    all_outdated_dates = []
    all_outdated_urls = []

    for table in tables:
        rows = parse_markdown_table(table)
        outdated_dates, outdated_urls = check_outdated_entries(rows, today, current_year)
        all_outdated_dates.extend(outdated_dates)
        all_outdated_urls.extend(outdated_urls)

    if all_outdated_dates:
        print("Outdated Date Entries:")
        for name, key, val in all_outdated_dates:
            print(f"- {name}: {key} = {val}")
    else:
        print("No outdated date entries found.")

    print("\nURLs with Outdated Years:")
    if all_outdated_urls:
        for name, url, year in all_outdated_urls:
            print(f"- {name}: {url} (year = {year})")
    else:
        print("No outdated URLs based on embedded years.")

if __name__ == "__main__":
    main()

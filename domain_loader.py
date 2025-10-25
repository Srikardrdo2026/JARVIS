import pandas as pd
import os
import webbrowser

DEFAULT_FILENAME = 'top10milliondomains.csv'

def load_domains(file_path=None, top_n=10000):
    """
    Load domains from CSV file, sorted by 'Rank', returning top N domains as a list.
    """
    if file_path is None:
        file_path = os.path.join(os.path.dirname(__file__), DEFAULT_FILENAME)
    try:
        df = pd.read_csv(file_path)
        df_sorted = df.sort_values('Rank').head(top_n)
        domains = df_sorted['Domain'].tolist()
        return domains
    except Exception as e:
        print(f"[ERROR] Failed to load domains from {file_path}: {e}")
        return []

def find_best_match(query, domains):
    """
    Find the best matching domain for the user query using exact or partial match.
    Returns a list of matched domain(s).
    """
    query = query.lower().replace("open ", "").strip()
    
    # Fallback: exact or partial match in domains list
    for domain in domains:
        if query == domain.lower() or query in domain.lower():
            return [domain]
    
    # No match found
    return []

def open_website(domain):
    """
    Open the domain in the default web browser.
    """
    url = f"https://{domain}"  # Use HTTPS for security
    webbrowser.open(url)
    print(f"Opening {url}...")
import os
import time
from flask import Flask, render_template, request, jsonify
import requests
import re
from bs4 import BeautifulSoup

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "contact-finder-secret-key")

def extract_contact_info(url, crawl_depth=0):
    """
    Extract contact information from a website.
    
    Args:
        url (str): The URL to extract contact info from
        crawl_depth (int): How many levels of pages to crawl (0 = just the main URL)
    
    Returns:
        dict: Dictionary with extracted contact information
    """
    try:
        # Initialize collections to store results
        all_emails = set()
        all_social_media = set()
        all_phones = set()
        all_names_titles = []
        visited_urls = set()
        urls_to_visit = [url]
        base_url = '/'.join(url.split('/')[:3])  # Get the base domain
        current_depth = 0
        
        # Set strict limits to prevent timeouts
        max_pages_per_level = 5  # Only process up to 5 pages per depth level
        request_timeout = 5      # 5 second timeout for each request
        total_page_limit = 10    # Maximum total pages to scan
        
        # Set up a session with headers to look like a browser
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        while urls_to_visit and current_depth <= crawl_depth and len(visited_urls) < total_page_limit:
            print(f"Processing depth level {current_depth}...")
            current_urls = urls_to_visit[:max_pages_per_level]  # Limit pages per level
            urls_to_visit = urls_to_visit[max_pages_per_level:] if len(urls_to_visit) > max_pages_per_level else []
            
            for current_url in current_urls:
                if current_url in visited_urls:
                    continue
                
                print(f"Scanning: {current_url}")
                visited_urls.add(current_url)
                
                try:
                    # Send HTTP request with timeout
                    response = session.get(current_url, timeout=request_timeout, allow_redirects=True)
                    
                    # Skip non-HTML content
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'text/html' not in content_type:
                        print(f"Skipping non-HTML content: {content_type}")
                        continue
                    
                    html_content = response.text
                    
                    # Parse with Beautiful Soup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Find all email addresses using regex
                    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    emails = set(re.findall(email_pattern, html_content))
                    all_emails.update(emails)
                    
                    # Find social media links
                    social_domains = [
                        'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
                        'youtube.com', 'pinterest.com', 't.me', 'wa.me', 'whatsapp.com',
                        'github.com', 'tiktok.com', 'snapchat.com', 'dribbble.com', 'behance.net'
                    ]
                    
                    # Use a more efficient approach for finding links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Skip empty links and JavaScript/mailto links
                        if not href or href.startswith(('javascript:', '#', 'mailto:')):
                            continue
                            
                        # Process social media links
                        if any(domain in href for domain in social_domains):
                            # Make sure we have absolute URLs
                            if href.startswith('/'):
                                href = base_url + href
                            elif not href.startswith(('http://', 'https://')):
                                href = current_url.rstrip('/') + '/' + href
                                
                            all_social_media.add(href)
                        
                        # For crawling: collect internal links (only if we need more pages)
                        if crawl_depth > 0 and current_depth < crawl_depth and len(urls_to_visit) < max_pages_per_level:
                            # Only process internal links
                            is_internal = False
                            
                            # Absolute URL to the same domain
                            if href.startswith(base_url):
                                is_internal = True
                                
                            # Relative URL
                            elif href.startswith('/'):
                                href = base_url + href
                                is_internal = True
                            
                            # Add to queue if it's internal and new
                            if is_internal and href not in visited_urls and href not in urls_to_visit:
                                # Skip common non-useful pages
                                if any(skip in href.lower() for skip in ['.pdf', '.jpg', '.png', '.gif', 'javascript:', '#', 'tel:']):
                                    continue
                                
                                urls_to_visit.append(href)
                    
                    # Process the main content more efficiently
                    # First, try to focus on contact-specific areas
                    contact_sections = soup.find_all(['div', 'section', 'footer'], 
                                                   class_=lambda c: c and any(keyword in str(c).lower() 
                                                                             for keyword in ['contact', 'footer', 'about']))
                    
                    # If we found contact sections, focus on those first
                    content_to_search = html_content
                    if contact_sections:
                        content_to_search = ' '.join(section.get_text() for section in contact_sections)
                    
                    # Find phone numbers
                    phone_pattern = r'(\+\d{1,3}[- ]?)?\(?\d{2,3}\)?[- ]?\d{3,4}[- ]?\d{3,4}'
                    phones = set(re.findall(phone_pattern, content_to_search))
                    
                    # Look for WA/Phone pattern
                    wa_phone_pattern = r'(?:WA|WhatsApp|Phone|Tel|Contact|Call|Mobile)(?:\s*(?:Number|No))?(?:\s*:|\s*=|\s*>)?\s*([+\d\s\-\(\)\.]{8,20})'
                    wa_phones = re.findall(wa_phone_pattern, content_to_search, re.IGNORECASE)
                    if wa_phones:
                        phones.update(wa_phones)
                    
                    # Extract name and title information from contact sections
                    name_title_pattern = r'([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})\s*(?:[-,:]|is\s+(?:our|the))?\s*([A-Z][a-zA-Za-z\s&]+(?:CEO|CTO|CFO|CIO|Director|Manager|President|Founder|Owner|Head|Lead|Chief|Principal|Partner|VP|Executive|Officer|Supervisor))'
                    name_titles = re.findall(name_title_pattern, content_to_search)
                    if name_titles:
                        all_names_titles.extend(name_titles)
                    
                except requests.exceptions.Timeout:
                    print(f"Request timed out for {current_url}")
                    continue
                except requests.exceptions.RequestException as e:
                    print(f"Request error for {current_url}: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing {current_url}: {e}")
                    continue
                
                # Sleep briefly between requests to be respectful
                time.sleep(0.5)
            
            current_depth += 1
        
        # Extract phone from WhatsApp links
        for link in all_social_media:
            if 'wa.me' in link:
                # Extract the phone number from WhatsApp link
                wa_num_match = re.search(r'wa\.me/(\+?\d+)', link)
                if wa_num_match:
                    all_phones.add(wa_num_match.group(1))
        
        # Filter out irrelevant phone numbers
        filtered_phones = []
        for phone in all_phones:
            # Ensure it looks like a real phone number (at least 8 digits)
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) >= 8:
                filtered_phones.append(phone)
        
        # Format name and title information
        formatted_people = []
        for name, title in all_names_titles:
            name = name.strip()
            title = title.strip()
            if name and title and len(name) > 3 and len(title) > 2:
                # Only add unique people
                person_entry = {'name': name, 'title': title}
                if person_entry not in formatted_people:
                    formatted_people.append(person_entry)
        
        return {
            'emails': list(all_emails),
            'social_media': list(set(all_social_media)),
            'phones': filtered_phones,
            'people': formatted_people,
            'scanned_pages': len(visited_urls),
            'success': True
        }
    except Exception as e:
        print(f"General error in extraction: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')
    
@app.route('/api/extract', methods=['POST'])
def extract():
    data = request.get_json()
    url = data.get('url', '')
    crawl_depth = int(data.get('crawl_depth', 0))  # Default to 0 (no crawling)
    
    # Validate input
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'})
    
    # Limit crawl depth for performance reasons
    if crawl_depth > 2:
        crawl_depth = 2  # Cap at 2 levels to prevent excessive crawling
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Extract contact information with the specified crawl depth
    result = extract_contact_info(url, crawl_depth)
    return jsonify(result)

@app.route('/api/export-csv', methods=['POST'])
def export_csv():
    """Generate and return a CSV file of the contact information"""
    import csv
    import io
    
    data = request.get_json()
    
    if not data or not data.get('success', False):
        return jsonify({'success': False, 'error': 'No valid data to export'})
    
    # Create a CSV in memory
    output = io.StringIO()
    csv_writer = csv.writer(output)
    
    # Write header row
    csv_writer.writerow(['Type', 'Value', 'Additional Info'])
    
    # Write email addresses
    for email in data.get('emails', []):
        csv_writer.writerow(['Email', email, ''])
    
    # Write phone numbers
    for phone in data.get('phones', []):
        csv_writer.writerow(['Phone', phone, ''])
    
    # Write social media links
    for link in data.get('social_media', []):
        # Determine the platform
        platform = 'Social Media'
        if 'facebook.com' in link:
            platform = 'Facebook'
        elif 'twitter.com' in link or 'x.com' in link:
            platform = 'Twitter/X'
        elif 'linkedin.com' in link:
            platform = 'LinkedIn'
        elif 'instagram.com' in link:
            platform = 'Instagram'
        elif 't.me' in link:
            platform = 'Telegram'
        elif 'wa.me' in link or 'whatsapp.com' in link:
            platform = 'WhatsApp'
        elif 'youtube.com' in link:
            platform = 'YouTube'
        elif 'github.com' in link:
            platform = 'GitHub'
        
        csv_writer.writerow(['Social', link, platform])
    
    # Write people information
    for person in data.get('people', []):
        csv_writer.writerow(['Person', person.get('name', ''), person.get('title', '')])
    
    # Write scan stats
    csv_writer.writerow(['Info', f'Scanned Pages: {data.get("scanned_pages", 1)}', ''])
    
    # Prepare response
    csv_content = output.getvalue()
    
    # Create a response with the CSV data
    response = app.response_class(
        response=csv_content,
        status=200,
        mimetype='text/csv'
    )
    
    # Set the content disposition header to suggest a filename
    response.headers["Content-Disposition"] = "attachment; filename=contact_info.csv"
    
    return response

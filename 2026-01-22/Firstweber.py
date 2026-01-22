import json
import time
from curl_cffi import requests
from parsel import Selector

# Setting up our basic scraper configuration
URL = "https://www.firstweber.com/CMS/CmsRoster/RosterSearchResults"
OUTPUT_FILE = "firstweber_agents.json"
PAGE_SIZE = 10

# Helper function to tidy up messy text (removes extra spaces and newlines)
def clean_text(text):
    if not text:
        return ""
    return text.replace("\r", " ").replace("\n", " ").strip()

# Helper to split a full name string into First, Middle, and Last names
def parse_name(full_name):
    if not full_name:
        return "", "", ""
    parts = full_name.split()
    first_name = parts[0] if parts else ""
    middle_name = ""
    last_name = ""
    if len(parts) > 2:
        middle_name = parts[1]
        last_name = " ".join(parts[2:])
    elif len(parts) == 2:
        last_name = parts[1]
    return first_name, middle_name, last_name

# These headers are CRITICAL. They make our script look exactly like a real Chrome browser.
BIO_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ml;q=0.8',
    'cache-control': 'max-age=0',
    'cookie': 'culture=en; currencyAbbr=USD; currencyCulture=en-US; _gcl_au=1.1.695186038.1768974934; _gid=GA1.2.1744770794.1768974934; _fbp=fb.1.1768974934969.704318463377616977; subsiteID=333277; subsiteDirectory=; ASP.NET_SessionId=ypbghjuz4ysmbhwkdn0jh4hg; _cfuvid=A.h2VNmglaVMAzjjFY4MgdebQ._pE68mPx.AQcmEnZg-1769057563349-0.0.1.1-604800000; __cf_bm=__h9aJzst9.I1OwoeI9LSIB4LXgQXo_CKI_NT5XPEgQ-1769063319-1.0.1.1-_0UHZjDtelJ3ZkEerYPnApUi0r7aCWn9YP._QyjQjVjDSNxh6Xf0W0zrQsuFPHzXGDiGLhRpKyDqJ7cnRrfZh1rbv8goFjYLh7pxWaxOKr8; cf_clearance=RA4Fh_2QmBMkBRotOWbze5bWsrY7is.1rSuoFN5ysy4-1769063323-1.2.1.1-wCyi5lvkQdVPCyd6WA6j9MRSlIJyC8XMyH3nRcXc.vaN6IzEgYB4eYkvEd3smjp0e2cwF_Q7J54P3r6zsE7eMEzh8hY9.meCGV5l2p37u_fm5nExMDiKZ4c4Fg5ufjl.swO3fEI9P4agnnRPFCxROJ__bNPx8AAhZVxPFiE4nhW4pIENl8iD23RTfjcp3RzUcJ0HPRhysi_vIco.w42JleI0uykR9gwXnIQOvsEOlTU; rnSessionID=334610933025978167; _ga_S72FPQ9FF0=GS2.1.s1769063319$o4$g1$t1769063324$j55$l0$h150153454; _ga=GA1.2.162978467.1768974934; _gat_gtag_UA_9279272_1=1',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"143.0.7499.169"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="143.0.7499.169", "Chromium";v="143.0.7499.169", "Not A(Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Linux"',
    'sec-ch-ua-platform-version': '""',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
}

# For the list, some headers are slightly different (XMLHttpRequest)
LIST_HEADERS = BIO_HEADERS.copy()
LIST_HEADERS["referer"] = "https://www.firstweber.com/roster/Agents"
LIST_HEADERS["accept"] = "application/json, text/javascript, */*; q=0.01"
LIST_HEADERS["x-requested-with"] = "XMLHttpRequest"
LIST_HEADERS["sec-fetch-dest"] = "empty"
LIST_HEADERS["sec-fetch-mode"] = "cors"
LIST_HEADERS.pop("sec-fetch-user", None)
LIST_HEADERS.pop("upgrade-insecure-requests", None)

def scrape_agents():
    agents = []
    
    # We will track pagination manually
    page_number = 1
    total_count = None

    print("--- Phase 1: Getting the Agent List ---")
    
    # Keep looping through pages until we have collected everyone
    while True:
        print(f"Fetching page {page_number}...")
        
        # Parameters to tell the server which page we want
        params = {
            "layoutID": "1126",
            "pageSize": str(PAGE_SIZE),
            "pageNumber": str(page_number),
            "sortBy": "firstname"
        }

        try:
            # Send the request pretending to be Chrome ('impersonate="chrome120"')
            response = requests.get(URL, params=params, headers=LIST_HEADERS, impersonate="chrome120")
            
            # If the server blocks us or errors out, stop.
            if response.status_code != 200:
                print(f"Failed to fetch page {page_number}: {response.status_code}")
                break

            # Parse the JSON response
            data = response.json()
            # Sometimes the JSON comes as a string inside the JSON, so we double-parse if needed
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    pass

            # Update the total count of agents (only needed once)
            if total_count is None:
                total_count = data.get("TotalCount", 0)
                print(f"Total Agents: {total_count}")

            # Grab the actual HTML containing the agent cards
            html_content = data.get("Html", "")
            if not html_content:
                print("No HTML content found. Stopping.")
                break

            # Use Parsel to find data within the HTML
            sel = Selector(text=html_content)
            
            # Find all agent card elements
            cards = sel.css('article.rng-agent-roster-agent-card')
            if not cards: cards = sel.css('.rn-agent-roster-item')
            
            if not cards:
                print("No agents found on this page. Stopping.")
                break

            # Loop through each agent card on the current page
            for card in cards:
                # 1. Get the Name
                name_text = card.css('h1.rn-agent-roster-name::text').get()
                full_name = clean_text(name_text)
                first, middle, last = parse_name(full_name)
                
                # 2. Get the Profile URL
                profile_path = card.css('a.button.hollow::attr(href)').get()
                profile_url = f"https://www.firstweber.com{profile_path}" if profile_path else "N/A"

                # 3. Get the Photo URL
                image_url = card.css('img::attr(src)').get()
                if image_url and not image_url.startswith("http"):
                    image_url = f"https://www.firstweber.com{image_url}"

                # 4. Get Office and Address
                office_name = clean_text(card.css('p strong::text').get())
                p_text_nodes = card.xpath('.//p//text()').getall()
                # Join address parts but skip the office name and 'Directions' text
                address_cleaned = " ".join([clean_text(t) for t in p_text_nodes if clean_text(t) and clean_text(t) != office_name and "Directions" not in t])
                address_cleaned = address_cleaned.rstrip(" |")
                


                # 5. Get Phone Numbers (using icon logic specific to FirstWeber)
                # Office phone usually has a building icon, let's try generic rni- or fallback to knowns
                # In debug card we saw 'rni-profile' for agent phone.
                
                office_phone_xp = card.xpath('.//i[contains(@class, "rni-building")]/parent::*/text()').getall() 
                if not office_phone_xp:
                     office_phone_xp = card.xpath('.//i[contains(@class, "fa-building")]/parent::*/text()').getall()
                office_phone = "".join([clean_text(t) for t in office_phone_xp])
                
                agent_phone_xp = card.xpath('.//i[contains(@class, "rni-profile")]/parent::*/text()').getall()
                if not agent_phone_xp: # Fallback to kentwood style just in case
                     agent_phone_xp = card.xpath('.//i[contains(@class, "fa-user")]/parent::*/text()').getall()
                     
                agent_phone = "".join([clean_text(t) for t in agent_phone_xp])
                
                office_phone = office_phone if office_phone else "N/A"
                agent_phone = agent_phone if agent_phone else "N/A"

                # 6. Get Social Media Links
                social_links = []
                social_elements = card.css('li.rng-agent-profile-contact-social a::attr(href)').getall()
                for link in social_elements:
                    if link:
                        social_links.append(link)

                # Store all extracted data in a dictionary
                agent = {
                    "first_name": first,
                    "middle_name": middle,
                    "last_name": last,
                    "profile_url": profile_url,
                    "image_url": image_url,
                    "office_name": office_name,
                    "address": address_cleaned,
                    "agent_phone_numbers": [agent_phone] if agent_phone != "N/A" else [],
                    "office_phone_numbers": [office_phone] if office_phone != "N/A" else [],
                    "social": social_links,
                    "description": "N/A", # Placeholder, will fill in Phase 2
                    "mail_id": "N/A"      
                }
                agents.append(agent)

            print(f"Collected {len(agents)} agents so far.")

            # Stop if we have collected everyone
            if len(agents) >= total_count:
                print("Reached total count.")
                break
            
            # Go to next page
            page_number += 1
            
            # (Optional) Safety break removed for final version
            # if page_number > 2:
            #     print("Stopping after 2 pages for safety/test.")
            #     break

        except Exception as e:
            print(f"Error on page {page_number}: {e}")
            break


    print("\n--- Phase 2: getting descriptions from profile pages... ---")
    
    # Now loop through the agents we found to get their bios
    count = 0
    for agent in agents:
        p_url = agent["profile_url"]
        if p_url == "N/A":
             continue
        
        count += 1
        print(f"[{count}/{len(agents)}] Visiting {p_url}...")
        
        try:
             # Prepare headers for the profile visit
             headers = BIO_HEADERS.copy()
             headers["referer"] = p_url # Mimic self-referencing
             
             # Fetch the profile page
             resp_bio = requests.get(p_url, headers=headers, impersonate="chrome120")
             
             if resp_bio.status_code == 200:
                 sel = Selector(text=resp_bio.text)
                 # Look for the bio using the generic 'widget-text' ID pattern
                 xpath = "//div[starts-with(@id, 'widget-text-1-preview-5503')]"
                 desc_node = sel.xpath(xpath)
                 
                 if desc_node:
                     text_content = desc_node.xpath(".//text()").getall()
                     desc_text = " ".join([t.strip() for t in text_content if t.strip()])
                     agent["description"] = desc_text
                     print("  > Description Found!")
                 else:
                     print("  > No description text found (Selector mismatch).")
             else:
                 print(f"  > Failed to load profile: {resp_bio.status_code}")
        
        except Exception as e:
            print(f"  > Error: {e}")
            
        # Wait a bit between requests so we don't get banned
        time.sleep(1.0)

    # Finally, save everything to our JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(agents)} agents to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_agents()

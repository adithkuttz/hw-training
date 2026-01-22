import json
import time
from curl_cffi import requests
from parsel import Selector

# ================= CONFIG =================
URL = "https://www.firstweber.com/CMS/CmsRoster/RosterSearchResults"
OUTPUT_FILE = "firstweber_agents.json"
PAGE_SIZE = 10

# ================= SESSION =================
# IMPORTANT: session keeps cookies automatically (DO NOT hardcode cookies)
session = requests.Session(impersonate="chrome120")

# ================= HELPERS =================
def clean_text(text):
    if not text:
        return ""
    return text.replace("\r", " ").replace("\n", " ").strip()

def parse_name(full_name):
    if not full_name:
        return "", "", ""
    parts = full_name.split()
    first = parts[0] if parts else ""
    middle = parts[1] if len(parts) > 2 else ""
    last = " ".join(parts[2:]) if len(parts) > 2 else (parts[1] if len(parts) == 2 else "")
    return first, middle, last

# ================= HEADERS =================
BIO_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

LIST_HEADERS = BIO_HEADERS.copy()
LIST_HEADERS.update({
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://www.firstweber.com/roster/Agents",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty"
})

# ================= SCRAPER =================
def scrape_agents():
    agents = []
    page_number = 1
    total_count = None

    print("\n--- PHASE 1: Agent List ---")

    while True:
        print(f"Fetching page {page_number}...")

        params = {
            "layoutID": "1126",
            "pageSize": PAGE_SIZE,
            "pageNumber": page_number,
            "sortBy": "firstname"
        }

        response = session.get(URL, params=params, headers=LIST_HEADERS)

        if response.status_code != 200:
            print("Blocked or error:", response.status_code)
            break

        data = response.json()
        if isinstance(data, str):
            data = json.loads(data)

        if total_count is None:
            total_count = data.get("TotalCount", 0)
            print("Total agents:", total_count)

        html = data.get("Html", "")
        if not html:
            break

        sel = Selector(text=html)
        cards = sel.css("article.rng-agent-roster-agent-card") or sel.css(".rn-agent-roster-item")

        if not cards:
            break

        for card in cards:
            full_name = clean_text(card.css("h1.rn-agent-roster-name::text").get())
            first, middle, last = parse_name(full_name)

            profile_path = card.css("a.button.hollow::attr(href)").get()
            profile_url = f"https://www.firstweber.com{profile_path}" if profile_path else "N/A"

            image_url = card.css("img::attr(src)").get()
            if image_url and not image_url.startswith("http"):
                image_url = f"https://www.firstweber.com{image_url}"

            office_name = clean_text(card.css("p strong::text").get())
            p_text = card.xpath(".//p//text()").getall()
            address = " ".join([
                clean_text(t) for t in p_text
                if clean_text(t) and clean_text(t) != office_name and "Directions" not in t
            ])

            agent_phone = "".join(card.xpath('.//i[contains(@class,"rni-profile")]/parent::*/text()').getall()).strip()
            office_phone = "".join(card.xpath('.//i[contains(@class,"rni-building")]/parent::*/text()').getall()).strip()

            socials = card.css("li.rng-agent-profile-contact-social a::attr(href)").getall()

            agents.append({
                "first_name": first,
                "middle_name": middle,
                "last_name": last,
                "profile_url": profile_url,
                "image_url": image_url,
                "office_name": office_name,
                "address": address,
                "agent_phone_numbers": [agent_phone] if agent_phone else [],
                "office_phone_numbers": [office_phone] if office_phone else [],
                "social": socials,
                "description": "N/A",
                "mail_id": "N/A"
            })

        print("Collected:", len(agents))

        if len(agents) >= total_count:
            break

        page_number += 1

    print("\n--- PHASE 2: Agent Bios ---")

    for i, agent in enumerate(agents, 1):
        if agent["profile_url"] == "N/A":
            continue

        print(f"[{i}/{len(agents)}] {agent['profile_url']}")
        headers = BIO_HEADERS.copy()
        headers["referer"] = agent["profile_url"]

        resp = session.get(agent["profile_url"], headers=headers)

        if resp.status_code == 200:
            sel = Selector(text=resp.text)
            node = sel.xpath("//div[starts-with(@id,'widget-text-1-preview')]")
            if node:
                text = " ".join(t.strip() for t in node.xpath(".//text()").getall() if t.strip())
                agent["description"] = text

        time.sleep(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=4, ensure_ascii=False)

    print("\nSaved:", OUTPUT_FILE)

# ================= RUN =================
if __name__ == "__main__":
    scrape_agents()

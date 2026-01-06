from arachnid.websites import HackerNews, BleepingComputer

def run(site):
    print(f"...Fetching: {site.__class__.__name__}")
    try:
        site.fetch_and_parse_xml()  # 1st method being called to fetch
        print(f"Articles Found: {len(site.extracted_data)}")
        for article in site.extracted_data:
            print(f"-> {article['title']}")
    except Exception as e:
        print(f"Error processing site - {site.__class__.__name__.upper()}: {e}")
        
def main():
    sites = [HackerNews(),
             BleepingComputer()]
    
    for site in sites:
        run(site)
    
#main()
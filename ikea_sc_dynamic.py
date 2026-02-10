import requests
import json
from datetime import datetime   

from db import insert_product

keyword = input("Enter item to search (e.g., sofa): ")

# COMPREHENSIVE KEYWORD CATEGORIZATION SYSTEM
# Maps user keywords to (search_term, category_name) tuples
KEYWORD_MAPPING = {
    # Sofas & Armchairs
    "sofa": ("sofas", "Sofas & Armchairs"),
    "sofas": ("sofas", "Sofas & Armchairs"),
    "armchair": ("armchairs", "Sofas & Armchairs"),
    "armchairs": ("armchairs", "Sofas & Armchairs"),
    "loveseat": ("2-seat sofas", "Sofas & Armchairs"),
    "sectional": ("modular sofas", "Sofas & Armchairs"),
    "couch": ("sofas", "Sofas & Armchairs"),
    "recliner": ("recliners", "Sofas & Armchairs"),
    "sofa bed": ("sofa-beds", "Sofas & Armchairs"),
    
    # Chairs & Dining
    "chair": ("chairs", "Chairs"),
    "chairs": ("chairs", "Chairs"),
    "stool": ("stools", "Chairs"),
    "stools": ("stools", "Chairs"),
    "bench": ("benches", "Chairs"),
    "benches": ("benches", "Chairs"),
    "dining chair": ("dining chairs", "Chairs"),
    "bar stool": ("bar stools", "Chairs"),
    "office chair": ("office chairs", "Chairs"),
    
    # Tables & Desks
    "table": ("tables", "Tables & Desks"),
    "tables": ("tables", "Tables & Desks"),
    "desk": ("desks", "Tables & Desks"),
    "desks": ("desks", "Tables & Desks"),
    "dining table": ("dining tables", "Tables & Desks"),
    "coffee table": ("coffee tables", "Tables & Desks"),
    "side table": ("side tables", "Tables & Desks"),
    "end table": ("side tables", "Tables & Desks"),
    "work desk": ("desks", "Tables & Desks"),
    "writing desk": ("desks", "Tables & Desks"),
    "computer desk": ("desks", "Tables & Desks"),
    
    # Beds & Mattresses
    "bed": ("beds", "Beds & Mattresses"),
    "beds": ("beds", "Beds & Mattresses"),
    "mattress": ("mattresses", "Beds & Mattresses"),
    "mattresses": ("mattresses", "Beds & Mattresses"),
    "bed frame": ("bed frames", "Beds & Mattresses"),
    "headboard": ("headboards", "Beds & Mattresses"),
    "bedroom": ("bedroom furniture", "Beds & Mattresses"),
    
    # Kitchenware & Tableware
    "kitchen": ("kitchenware", "Kitchenware & Tableware"),
    "kitchenware": ("kitchenware", "Kitchenware & Tableware"),
    "tableware": ("tableware", "Kitchenware & Tableware"),
    "plate": ("plates", "Kitchenware & Tableware"),
    "plates": ("plates", "Kitchenware & Tableware"),
    "bowl": ("bowls", "Kitchenware & Tableware"),
    "bowls": ("bowls", "Kitchenware & Tableware"),
    "spoon": ("spoons", "Kitchenware & Tableware"),
    "spoons": ("spoons", "Kitchenware & Tableware"),
    "fork": ("forks", "Kitchenware & Tableware"),
    "forks": ("forks", "Kitchenware & Tableware"),
    "knife": ("knives", "Kitchenware & Tableware"),
    "knives": ("knives", "Kitchenware & Tableware"),
    "cup": ("cups", "Kitchenware & Tableware"),
    "cups": ("cups", "Kitchenware & Tableware"),
    "mug": ("mugs", "Kitchenware & Tableware"),
    "mugs": ("mugs", "Kitchenware & Tableware"),
    "glass": ("glasses", "Kitchenware & Tableware"),
    "glasses": ("glasses", "Kitchenware & Tableware"),
    "cookware": ("cookware", "Kitchenware & Tableware"),
    "pan": ("pans", "Kitchenware & Tableware"),
    "pot": ("pots", "Kitchenware & Tableware"),
    "utensil": ("utensils", "Kitchenware & Tableware"),
    "utensils": ("utensils", "Kitchenware & Tableware"),
    
    # Storage & Organisation
    "storage": ("storage", "Storage & Organization"),
    "organisation": ("storage", "Storage & Organization"),
    "organizers": ("storage", "Storage & Organization"),
    "wardrobe": ("wardrobes", "Storage & Organization"),
    "wardrobes": ("wardrobes", "Storage & Organization"),
    "shelf": ("shelves", "Storage & Organization"),
    "shelves": ("shelves", "Storage & Organization"),
    "cabinet": ("cabinets", "Storage & Organization"),
    "cabinets": ("cabinets", "Storage & Organization"),
    "drawer": ("drawers", "Storage & Organization"),
    "drawers": ("chest of drawers", "Storage & Organization"),
    "basket": ("storage baskets", "Storage & Organization"),
    "box": ("storage boxes", "Storage & Organization"),
    "container": ("storage containers", "Storage & Organization"),
    
    # Outdoor
    "outdoor": ("outdoor", "Outdoor"),
    "garden": ("outdoor", "Outdoor"),
    "patio": ("outdoor furniture", "Outdoor"),
    "balcony": ("outdoor furniture", "Outdoor"),
    "terrace": ("outdoor furniture", "Outdoor"),
    "outdoor chair": ("outdoor chairs", "Outdoor"),
    "outdoor table": ("outdoor tables", "Outdoor"),
    
    # Baby & Children
    "baby": ("baby", "Baby & Children"),
    "children": ("children", "Baby & Children"),
    "kids": ("children", "Baby & Children"),
    "child": ("children", "Baby & Children"),
    "crib": ("cribs", "Baby & Children"),
    "high chair": ("high chairs", "Baby & Children"),
    "toy": ("toys", "Baby & Children"),
    "toys": ("toys", "Baby & Children"),
    
    # Study & Office
    "study": ("desks", "Tables & Desks"),
    "office": ("office furniture", "Tables & Desks"),
    
    # Lighting
    "lighting": ("lighting", "Lighting"),
    "lamp": ("lamps", "Lighting"),
    "lamps": ("lamps", "Lighting"),
    "shade": ("lamp shades", "Lighting"),
    "shades": ("lamp shades", "Lighting"),
    "ceiling lamp": ("ceiling lamps", "Lighting"),
    "floor lamp": ("floor lamps", "Lighting"),
    "table lamp": ("table lamps", "Lighting"),
    
    # Textiles & Rugs
    "textile": ("textiles", "Textiles & Rugs"),
    "textiles": ("textiles", "Textiles & Rugs"),
    "rug": ("rugs", "Textiles & Rugs"),
    "rugs": ("rugs", "Textiles & Rugs"),
    "carpet": ("rugs", "Textiles & Rugs"),
    "blanket": ("blankets", "Textiles & Rugs"),
    "pillow": ("pillows", "Textiles & Rugs"),
    "cushion": ("cushions", "Textiles & Rugs"),
    
    # Curtains & Blinds
    "curtain": ("curtains", "Curtains & Blinds"),
    "curtains": ("curtains", "Curtains & Blinds"),
    "blind": ("blinds", "Curtains & Blinds"),
    "blinds": ("blinds", "Curtains & Blinds"),
    
    # Decoration
    "decoration": ("decoration", "Decoration"),
    "decor": ("decoration", "Decoration"),
    "vase": ("vases", "Decoration"),
    "picture": ("pictures", "Decoration"),
    "frame": ("frames", "Decoration"),
    "mirror": ("mirrors", "Decoration"),
    "candle": ("candles", "Decoration"),
    
    # Plants
    "plant": ("plants", "Plants & Planters"),
    "plants": ("plants", "Plants & Planters"),
    "planter": ("planters", "Plants & Planters"),
    "planters": ("planters", "Plants & Planters"),
    "flower": ("artificial flowers", "Plants & Planters"),
    
    # Bathroom
    "bathroom": ("bathroom", "Bathroom"),
    "bath": ("bathroom", "Bathroom"),
    "shower": ("shower", "Bathroom"),
    "toilet": ("bathroom", "Bathroom"),
    "sink": ("bathroom sinks", "Bathroom"),
    "towel": ("towels", "Bathroom"),
    "towel rack": ("towel racks", "Bathroom"),
    "towel holder": ("towel racks", "Bathroom"),
    
    # Laundry & Cleaning
    "laundry": ("laundry", "Laundry & Cleaning"),
    "cleaning": ("cleaning", "Laundry & Cleaning"),
    "detergent": ("cleaning", "Laundry & Cleaning"),
    "hanger": ("hangers", "Laundry & Cleaning"),
    "laundry basket": ("laundry baskets", "Laundry & Cleaning"),
    
    # Electronics
    "electronics": ("electronics", "Electronics"),
    "tv": ("tv", "Electronics"),
    "speaker": ("speakers", "Electronics"),
    "radio": ("radios", "Electronics"),
    
    # Smart Home
    "smart": ("smart home", "Smart Home"),
    "home smart": ("smart home", "Smart Home"),
    "automation": ("smart home", "Smart Home"),
    
    # Home Improvement
    "home improvement": ("tools", "Home Improvement"),
    "tool": ("tools", "Home Improvement"),
    "tools": ("tools", "Home Improvement"),
    "hardware": ("hardware", "Home Improvement"),
    
    # Food & Beverages
    "food": ("food", "Food & Beverages"),
    "beverage": ("beverages", "Food & Beverages"),
    "beverages": ("beverages", "Food & Beverages"),
    "snack": ("snacks", "Food & Beverages"),
    "drink": ("drinks", "Food & Beverages"),
}

# Determine search term and category
input_keyword = keyword.lower()
if input_keyword in KEYWORD_MAPPING:
    search_term, category_name = KEYWORD_MAPPING[input_keyword]
else:
    # If keyword not in mapping, use as-is
    search_term = input_keyword
    category_name = input_keyword.title()

# IKEA Search API Configuration
url = "https://sik.search.blue.cdtapps.com/sg/en/search-result-page"

params = {
    "types": "PRODUCT",
    "q": search_term
}

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/plain;charset=UTF-8",
    "dnt": "1",
    "origin": "https://www.ikea.com",
    "priority": "u=1, i",
    "referer": "https://www.ikea.com/",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-gpc": "1",
    "session-id": "695776b2-d4a6-4d5e-97a8-fa7aa11f53c2",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
}

# Make API request
try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    # Check for results
    if 'searchResultPage' in data and 'products' in data['searchResultPage']:
        products = data['searchResultPage']['products']
        items = products.get('main', {}).get('items', [])
        
        if items:
            # Process each item silently
            for item in items:
                product = item.get('product', {})
                
                # Extract product details
                product_name = product.get('name', 'Unknown')
                product_price = product.get('priceNumeral', product.get('salesPrice', {}).get('numeral', 0))
                product_currency = product.get('currencyCode', product.get('salesPrice', {}).get('currencyCode', 'SGD'))
                
                # Build IKEA product URL
                product_id = product.get('id', '')
                product_url = None
                if product_id:
                    product_name_slug = product_name.lower().replace(' ', '-').replace('/', '-')
                    product_url = f"https://www.ikea.com/sg/en/p/{product_name_slug}-{product_id}/"
                
                # Convert currency to CNY if needed
                if product_currency.upper() != "CNY":
                    try:
                        rate_response = requests.get(
                            f"https://api.exchangerate-api.com/v4/latest/{product_currency}",
                            timeout=5
                        )
                        rate_data = rate_response.json()
                        rate = rate_data['rates']['CNY']
                        product_price = float(product_price) * rate
                        product_currency = "RMB"
                    except:
                        pass
                
                # Insert into database silently
                insert_product(
                    "IKEA",
                    product_name,
                    float(product_price),
                    product_currency,
                    datetime.now(),
                    category_name,
                    product_url
                )

except:
    pass  # Silent error handling
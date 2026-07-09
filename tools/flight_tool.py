import os
import re
import certifi
import requests
import airportsdata
import pycountry
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "MAA")


BASE_URL = "https://api.aviationstack.com/v1/flights"


AIRPORTS = airportsdata.load("IATA")

COUNTRY_ALIASES = {
    "usa": "US",
    "u.s.a": "US",
    "u.s.": "US",
    "america": "US",
    "united states": "US",
    "uk": "GB",
    "u.k.": "GB",
    "britain": "GB",
    "england": "GB",
    "great britain": "GB",
    "uae": "AE",
    "dubai": "AE",
    "united arab emirates": "AE",
    "south korea": "KR",
    "korea": "KR",
    "north korea": "KP",
    "india": "IN",
    "bharat": "IN",
    "china": "CN",
    "prc": "CN",
    "japan": "JP",
    "germany": "DE",
    "deutschland": "DE",
    "france": "FR",
    "spain": "ES",
    "espana": "ES",
    "italy": "IT",
    "italia": "IT",
    "russia": "RU",
    "russian federation": "RU",
    "canada": "CA",
    "australia": "AU",
    "brazil": "BR",
    "brasil": "BR",
    "mexico": "MX",
    "netherlands": "NL",
    "holland": "NL",
    "switzerland": "CH",
    "swiss": "CH",
    "sweden": "SE",
    "norway": "NO",
    "denmark": "DK",
    "finland": "FI",
    "singapore": "SG",
    "malaysia": "MY",
    "thailand": "TH",
    "vietnam": "VN",
    "indonesia": "ID",
    "philippines": "PH",
    "saudi arabia": "SA",
    "ksa": "SA",
    "qatar": "QA",
    "kuwait": "KW",
    "turkey": "TR",
    "türkiye": "TR",
    "egypt": "EG",
    "south africa": "ZA",
    "nigeria": "NG",
    "kenya": "KE",
    "new zealand": "NZ",
    "nz": "NZ",
    "ireland": "IE",
    "portugal": "PT",
    "greece": "GR",
    "poland": "PL",
    "austria": "AT",
    "belgium": "BE",
    "sri lanka": "LK",
    "bangladesh": "BD",
    "pakistan": "PK",
    "nepal": "NP",
    "hong kong": "HK",
    "taiwan": "TW",
    "israel": "IL",
}

CITY_MAIN_AIRPORTS = {
    # India
    "chennai": "MAA",
    "mumbai": "BOM",
    "bombay": "BOM",
    "delhi": "DEL",
    "new delhi": "DEL",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "hyderabad": "HYD",
    "kolkata": "CCU",
    "calcutta": "CCU",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "goa": "GOI",
    "kochi": "COK",
    "cochin": "COK",
    "trivandrum": "TRV",
    "thiruvananthapuram": "TRV",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "coimbatore": "CJB",
    "madurai": "IXM",
    "visakhapatnam": "VTZ",
    "nagpur": "NAG",
    "indore": "IDR",
    "chandigarh": "IXC",
    "bhubaneswar": "BBI",
    "guwahati": "GAU",
    "varanasi": "VNS",
    "amritsar": "ATQ",

    # Middle East
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "doha": "DOH",
    "riyadh": "RUH",
    "jeddah": "JED",
    "kuwait city": "KWI",
    "muscat": "MCT",
    "manama": "BAH",

    # US
    "new york": "JFK",
    "nyc": "JFK",
    "los angeles": "LAX",
    "chicago": "ORD",
    "san francisco": "SFO",
    "boston": "BOS",
    "washington": "IAD",
    "washington dc": "IAD",
    "seattle": "SEA",
    "miami": "MIA",
    "dallas": "DFW",
    "atlanta": "ATL",
    "houston": "IAH",
    "las vegas": "LAS",

    # UK / Europe
    "london": "LHR",
    "paris": "CDG",
    "frankfurt": "FRA",
    "amsterdam": "AMS",
    "madrid": "MAD",
    "rome": "FCO",
    "milan": "MXP",
    "zurich": "ZRH",
    "vienna": "VIE",
    "istanbul": "IST",
    "moscow": "SVO",
    "berlin": "BER",
    "munich": "MUC",
    "barcelona": "BCN",
    "lisbon": "LIS",
    "dublin": "DUB",
    "brussels": "BRU",
    "copenhagen": "CPH",
    "stockholm": "ARN",
    "oslo": "OSL",
    "helsinki": "HEL",
    "athens": "ATH",
    "warsaw": "WAW",

    # Asia-Pacific
    "singapore": "SIN",
    "hong kong": "HKG",
    "tokyo": "HND",
    "osaka": "KIX",
    "seoul": "ICN",
    "beijing": "PEK",
    "shanghai": "PVG",
    "bangkok": "BKK",
    "kuala lumpur": "KUL",
    "jakarta": "CGK",
    "manila": "MNL",
    "ho chi minh city": "SGN",
    "hanoi": "HAN",
    "sydney": "SYD",
    "melbourne": "MEL",
    "auckland": "AKL",
    "colombo": "CMB",
    "dhaka": "DAC",
    "kathmandu": "KTM",
    "karachi": "KHI",
    "lahore": "LHE",
    "islamabad": "ISB",
    "male": "MLE",

    # Africa
    "cairo": "CAI",
    "johannesburg": "JNB",
    "cape town": "CPT",
    "nairobi": "NBO",
    "lagos": "LOS",
    "casablanca": "CMN",

    # South America
    "sao paulo": "GRU",
    "rio de janeiro": "GIG",
    "buenos aires": "EZE",
    "mexico city": "MEX",
    "bogota": "BOG",
    "lima": "LIM",
    "santiago": "SCL",

    # Canada
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
}

COUNTRY_MAIN_AIRPORT = {
    # Country code to main airport IATA code mapping
    "IN": "DEL",    # India - Delhi
    "US": "JFK",    # USA - New York
    "GB": "LHR",    # UK - London
    "AE": "DXB",    # UAE - Dubai
    "KR": "ICN",    # South Korea - Seoul
    "CN": "PEK",    # China - Beijing
    "JP": "HND",    # Japan - Tokyo
    "DE": "FRA",    # Germany - Frankfurt
    "FR": "CDG",    # France - Paris
    "ES": "MAD",    # Spain - Madrid
    "IT": "FCO",    # Italy - Rome
    "RU": "SVO",    # Russia - Moscow
    "CA": "YYZ",    # Canada - Toronto
    "AU": "SYD",    # Australia - Sydney
    "BR": "GRU",    # Brazil - São Paulo
    "MX": "MEX",    # Mexico - Mexico City
    "NL": "AMS",    # Netherlands - Amsterdam
    "CH": "ZRH",    # Switzerland - Zurich
    "SE": "ARN",    # Sweden - Stockholm
    "NO": "OSL",    # Norway - Oslo
    "DK": "CPH",    # Denmark - Copenhagen
    "FI": "HEL",    # Finland - Helsinki
    "SG": "SIN",    # Singapore
    "MY": "KUL",    # Malaysia - Kuala Lumpur
    "TH": "BKK",    # Thailand - Bangkok
    "VN": "SGN",    # Vietnam - Ho Chi Minh City
    "ID": "CGK",    # Indonesia - Jakarta
    "PH": "MNL",    # Philippines - Manila
    "SA": "RUH",    # Saudi Arabia - Riyadh
    "QA": "DOH",    # Qatar - Doha
    "KW": "KWI",    # Kuwait
    "TR": "IST",    # Turkey - Istanbul
    "EG": "CAI",    # Egypt - Cairo
    "ZA": "JNB",    # South Africa - Johannesburg
    "NG": "LOS",    # Nigeria - Lagos
    "KE": "NBO",    # Kenya - Nairobi
    "NZ": "AKL",    # New Zealand - Auckland
    "IE": "DUB",    # Ireland - Dublin
    "PT": "LIS",    # Portugal - Lisbon
    "GR": "ATH",    # Greece - Athens
    "PL": "WAW",    # Poland - Warsaw
    "AT": "VIE",    # Austria - Vienna
    "BE": "BRU",    # Belgium - Brussels
    "LK": "CMB",    # Sri Lanka - Colombo
    "BD": "DAC",    # Bangladesh - Dhaka
    "PK": "KHI",    # Pakistan - Karachi
    "NP": "KTM",    # Nepal - Kathmandu
    "HK": "HKG",    # Hong Kong
    "TW": "TPE",    # Taiwan - Taipei
    "IL": "TLV",    # Israel - Tel Aviv
}

def clean_text(text:str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    stop_words =[
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"
    ]

    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words).strip()


def country_name_to_code(text:str):
    text = clean_text(text)

    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]

    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass

    for country in pycountry.countries:
        country_name = country.name.lower()
        if country_name in text:
            return country.alpha_2

    for alias, code in COUNTRY_ALIASES.items():
        if alias in text:
            return code


    return None   


def airport_country_matches(airport:dict, country_code:str) -> bool:
    airport_country = str(airport.get("country", "")).upper().strip()


    if airport_country == country_code:
        return True

    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country and airport_country.lower() == country.name.lower():
            return True
    except LookupError:
        pass

    return False  


def get_best_airport_for_country(country_code:str):
    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)


    if preferred and preferred in AIRPORTS:
        return preferred


    candidates =[]

    for iata, airport in AIRPORTS.items():
        if not iata:
            continue

        if airport_country_matches(airport, country_code):
            name = str(airport.get("name", "")).lower()
            city = str(airport.get("city", "")).lower()

            score = 0

            if "international" in name:
                score += 50

            if "intl" in name:
                score += 40
            if "capital" in name:
                score += 20
            if city:
                score += 5


            candidates.append((score, iata))
    if not candidates:
        return None


    candidates.sort(reverse=True)
    return candidates[0][1]



def resolve_location_to_iata(location: str):
    """
    Converts country/city/airport/IATA into IATA code.

    Examples:
    Bangladesh -> DAC
    Japan -> NRT
    Dhaka -> DAC
    Tokyo -> NRT
    DAC -> DAC
    """

    if not location:
        return None

    raw_location = location.strip()

    # Direct IATA code
    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)

    if not location_clean:
        return None

    # City preferred airport
    if location_clean in CITY_MAIN_AIRPORTS:
        return CITY_MAIN_AIRPORTS[location_clean]

    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
        if airport:
            return airport

    # Exact city match from airport database
    city_matches = []

    for iata, airport in AIRPORTS.items():
        city = str(airport.get("city", "")).lower().strip()
        name = str(airport.get("name", "")).lower().strip()

        score = 0

        if city == location_clean:
            score += 100
        elif location_clean in city:
            score += 70

        if location_clean in name:
            score += 50

        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]

    return None




def find_location_mentions(query: str):
    """
    Finds country or city names inside a natural language query.
    """

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", q):
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"\b{re.escape(name)}\b", q):
            mentions.append(name)

    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORTS:
        if re.search(rf"\b{re.escape(city)}\b", q):
            mentions.append(city)

    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions


def parse_route(query: str):
    """
    Returns:
    dep_iata, arr_iata

    Can return:
    None, None  -> global live flights
    DAC, NRT    -> filtered route
    DAC, None   -> all flights from DAC
    None, NRT   -> all flights to NRT
    """

    q = query.strip()
    q_lower = q.lower()

    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]

    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # Direct IATA code route: DAC to NRT
    codes = re.findall(r"\b[A-Z]{3}\b", q)

    if len(codes) >= 2:
        dep = codes[0].upper()
        arr = codes[1].upper()
        return dep, arr

    # Pattern: from X to Y
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        origin_text = match.group(1)
        dest_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: to Y from X
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dest_text = match.group(1)
        origin_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: flights from X
    match = re.search(r"\bfrom\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        origin_text = match.group(1)
        dep_iata = resolve_location_to_iata(origin_text)
        return dep_iata, None

    # Pattern: flights to X
    match = re.search(r"\bto\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        dest_text = match.group(1)
        arr_iata = resolve_location_to_iata(dest_text)
        return None, arr_iata

    # Fallback: find country/city mentions
    mentions = find_location_mentions(q)

    if len(mentions) >= 2:
        dep_iata = resolve_location_to_iata(mentions[0])
        arr_iata = resolve_location_to_iata(mentions[1])
        return dep_iata, arr_iata

    if len(mentions) == 1:
        arr_iata = resolve_location_to_iata(mentions[0])
        return DEFAULT_ORIGIN_IATA, arr_iata

    return None, None


def format_flight(flight: dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()


def search_flights(query: str, limit: int = 10):
    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(query)

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed: {e}"
    except ValueError:
        return "Flight API returned invalid JSON."

    if "error" in data:
        error = data["error"]
        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    flight_data = data.get("data", [])

    if not flight_data:
        route_text = ""

        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"

        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )

    route_info = "Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Live flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Live flights to {arr_iata}"

    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]

    return f"{route_info}\n\n" + "\n\n---\n\n".join(formatted_flights)


if __name__ == "__main__":
    print(search_flights("Plan a 7 days Japan trip from Bangladesh"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info"))

                    
#from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights


res = search_flights("plan 7 days trip from chennai to mumbai")
print(res)
#from tools.tavily_tool import tavily_search
#from tools.flight_tool import search_flights
from backend import run_travel_agent

# res = search_flights("plan 7 days trip from chennai to mumbai")
# print(res)

user_input= input("Enter travel request")

response = run_travel_agent(
    user_input=user_input,
    thread_id="test_user"
)
print("\nFINAL RESPONSE:\n")
print(response["answer"])
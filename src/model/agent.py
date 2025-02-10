
from dotenv import load_dotenv
from groq import Groq
import json
from datetime import datetime



#---------------------------------------------GROQCLOUD PART------------------------------------------------------------------
#get the api key from the environment variable
#GROQ_API_KEY = os.getenv("GROQ_API_KEY")
load_dotenv()

#using the llama-3.1-8b model
MODEL = "llama-3.1-8b-instant"

#init the Groqcloud client
client = Groq()




#---------------------------------------------TOOL PART------------------------------------------------------------------
#Find restaurants based on criteria (help user decide on a restaurant)-TOOL 1

# def find_restuarants(criteria:dict,RESTAURANTS:list) -> list:
#     """Search for restaurants that match the given criteria.
#     Expected criteria keys: cuisine, location, seating.
#     Returns a list of matching restaurants.    
#     """
    
#     matched_restaurants = []
#     for r in RESTAURANTS:
        
#         #match cuisine if specified
#         if "cuisine" in criteria and criteria["cuisine"]:
#             if criteria["cuisine"].lower() != r["cuisine"].lower():
#                 continue
        
#         #match seating if specified 
#         if "seating" in criteria and criteria["seating"]:
#             if criteria["seating"].lower() not in [s.lower() for s in r["seating"]]:
#                 continue
        
#         if "location" in criteria and criteria["location"]:
#             if criteria["location"].lower() != r["location"].lower():
#                 continue
#         matched_restaurants.append(r)
        
#     if matched_restaurants:
#         result_text = "Here are some restaurants that match your criteria:\n"
#         for r in matched_restaurants:
#             result_text += (f"- **{r['location']}** (Cuisines: {', '.join(r['cuisine'])}, "
#                             f"Seating: {', '.join(r['seating'])})\n")
#     else:
#         result_text = "I couldn't find any matching restaurants."

#     return result_text 

def find_restuarants(criteria: dict, RESTAURANTS: list) -> str:
    """
    Search for restaurants that match the given criteria.
    Expected criteria keys: cuisine, location, seating.
    Returns a formatted string with matching restaurants.
    """
    matched_restaurants = []
    
    for r in RESTAURANTS:
        # Process cuisine criteria: allow for either string or list input.
        if "cuisine" in criteria and criteria["cuisine"]:
            cuisine_value = criteria["cuisine"]
            if not isinstance(cuisine_value, list):
                cuisine_value = [cuisine_value]
            # Convert all provided cuisine values to lowercase.
            cuisine_value = [val.lower() for val in cuisine_value if isinstance(val, str)]
            # Convert the restaurant's cuisines (a list) to lowercase.
            restaurant_cuisines = [c.lower() for c in r["cuisine"] if isinstance(c, str)]
            # If none of the criteria cuisines are found in the restaurant's cuisines, skip this restaurant.
            if not any(val in restaurant_cuisines for val in cuisine_value):
                continue

        # Process seating criteria
        if "seating" in criteria and criteria["seating"]:
            seating_value = criteria["seating"]
            if not isinstance(seating_value, list):
                seating_value = [seating_value]
            seating_value = [val.lower() for val in seating_value if isinstance(val, str)]
            restaurant_seating = [s.lower() for s in r["seating"] if isinstance(s, str)]
            if not any(val in restaurant_seating for val in seating_value):
                continue

        # Process location criteria: if provided as a list, take the first element.
        if "location" in criteria and criteria["location"]:
            location_value = criteria["location"]
            if isinstance(location_value, list):
                location_value = location_value[0]
            if location_value.lower() != r["location"].lower():
                continue
        
        matched_restaurants.append(r)
        
    # Build a formatted string with matching restaurants.
    if matched_restaurants:
        result_text = "Here are some restaurants that match your criteria:\n"
        for r in matched_restaurants:
            result_text += (
                f"- **{r['location']}** (Cuisines: {', '.join(r['cuisine'])}, "
                f"Seating: {', '.join(r['seating'])})\n"
            )
    else:
        result_text = "I couldn't find any matching restaurants."
    
    return result_text



#make reservation at a restaurant -TOOL 2

def make_reservation(restaurant_id:int, location:str,  name:str,  date:str,time_slot:str, num_guests:int,cuisine:str,seating:str, RESTAURANTS:list)-> str:
    
    """Simulate making a reservation at the given restaurant.
    In a real-world scenario, this function would interact with a database or the reservation system of the restaurant. 
       
    """
     # Try location-based matching first, if a location is provided.
    restaurant = None
    if location:
        restaurant = next((r for r in RESTAURANTS if r["location"].lower() == location.lower()), None)

    # If no location match, fall back to restaurant ID.
    if not restaurant and restaurant_id is not None:
        restaurant = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)

    if not restaurant:
        return "Restaurant not found using the provided information."

    confirmation = (
        f"Reservation confirmed at {restaurant['location']} for {num_guests} guests on {date} at {time_slot}. The chosen cuisine is {cuisine} with {seating} seating arrangement."
        f"Thank you, {name}! We look forward to seeing you."
    )
    return confirmation
    
    
    
    
#---------------------------------------------MODEL PART------------------------------------------------------------------  
# System prompt for the Agent
def system_prompt() -> str:
    current_date = datetime.today().strftime('%Y-%m-%d')
    
    sys_prompt = f"""
    You are FoodieBot, an AI assistant for FoodieSpot restaurants.
    Your tasks are:
    - Find restaurants based on the user's specified cuisine and seating preferences. Always use available tools to search, list, and recommend restaurant options for the user to choose from.
    - Make reservations by collecting the customer's name, reservation date(must be after the date {current_date}), preferred time slot (between 11:00 and 22:00) and guest count.
    - For time slots, accept inputs in either 12-hour (e.g., '5pm') or 24-hour (e.g., '17:00') format. Convert any 12-hour input to 24-hour format to ensure the time falls between 11:00 and 22:00. If the converted time is outside this range, ask the user for a valid time.
    - When requested or after completing a reservation, display existing reservations in a Markdown table with columns: Name, Date, Time Slot, Number of Guests, Restaurant, Seating, and Cuisine.

    Rules:
    - Only assist with FoodieSpot reservations; if unrelated, reply: 
      "Unfortunately, I can only assist with FoodieSpot restaurant reservations."
    - Always respond as a JSON object with "intent", "parameters", and "response".
    - "intent" must be "find_restaurant", "make_reservation", or "chat". Do not reference internal function names or tool calls (find_restaurant, make_reservation) in your output.
    - Do not assume or generate missing details; only use what the user provides or retrieved via tools.
    - For every new reservation request, if any essential detail (cuisine, seating, customer name, date, time slot, or number of guests) is missing, ask the user to provide it. If any detail is already known from previous reservations, ask the user whether to reuse the known value or provide a new one. Always confirm all details with the user before finalizing the reservation.
    - 
    - Prevent duplicate bookings: if a reservation exactly matches an existing one (same date, restaurant, time slot, and seating), notify the user that it is already booked.


    Example output:
    {{
        "intent": "find_restaurant",
        "parameters":{{"cuisine": "Italian", "seating": "outdoor"}},
        "response": "I found a FoodieSpot restaurant with outdoor seating. Would you like me to book a table?"
    }}

    If unsure, default to "chat" with a polite response.
    """
    return sys_prompt.strip()
  
   
    



#Define the avaiblable tools before calling the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "find_restaurants",
            "description": "Search for restaurants based on cuisine, location, and seating preferences.",
            "parameters": {
                "type": "object",
                "properties": {
                    "criteria": {
                        "type": "object",
                        "description": "A dictionary containing keys like cuisine, location, and seating.",
                        "properties": {
                            "cuisine": {"type": "string", "description": "Type of cuisine (e.g., Italian, Chinese)"},
                            "location": {"type": "string", "description": "Restaurant location"},
                            "seating": {"type": "string", "description": "Seating preference (e.g., indoor, rooftop)"},
                        }
                    }
                },
                "required": ["criteria"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "make_reservation",
            "description": "Book a table at a restaurant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer", "description": "Restaurant ID"},
                    "location": {"type": "string", "description": "Restaurant location"},
                    "name": {"type": "string", "description": "Customer's name"},
                    "date": {"type": "string", "description": "Date of reservation (YYYY-MM-DD)"},
                    "time_slot": {"type": "string", "description": "Time of reservation"},
                    "num_guests": {"type": "integer", "description": "Number of guests"},
                    "cuisine" :{"type": "string", "description": "Type of cuisine chosen by the user." },
                    "seating" :{"type" : " string", "description": "Type of seating arrangement chosen by the user"},
                },
                "required": ["restaurant_id", "location", "cuisine", "name", "date", "time_slot", "num_guests","cuisine", "seating"],
            },
        },
    }
]



# Function to call the Model/Agent

def call_groq_llama(conversation_history, user_message,RESTAURANTS:list):
    sys_prompt = [{"role":"system", "content":system_prompt()}]
    messages = sys_prompt + conversation_history + [{"role": "user", "content": user_message}]
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "tools" : tools,
        "tool_choice" : "auto",
        #"response_format" : {"type": "json_object"}
    }
    
    try:
        response = client.chat.completions.create(**payload)
    except Exception as e:
        return {"intent": "chat", "parameters": {}, "response": "Error reaching the service. I apologize for the inconvenience. Please try again later."}
    
    
    
    #extract the the first choice from the response:
    print(response.choices[0].message)
    
    response_message = response.choices[0].message
    
    #if content is None and tool_calls are provided, process tool calls 
    if response_message.content is None and response_message.tool_calls:
    
    #tool_calls = response_message.tool_calls if hasattr(response_message, "tool_calls") else None
        
        #define a mappig from tool calls names to respective functions
        available_functions = {
            "find_restaurants": find_restuarants,
            "make_reservation": make_reservation
        }
        
        #append the initial(possibly empty) message to the coversation
        messages.append({"role":"assistant","content":response_message if response_message is not None else ""})
        
        # Process each tool call from the LLM.
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments)
               
            except Exception:
                function_args = {}
                
        
            
            # Call the appropriate function based on the tool call.
            if function_name == "find_restaurants":
                tool_result = available_functions[function_name](function_args.get("criteria", {}), RESTAURANTS)
               
            elif function_name == "make_reservation":
                #convert restaurant_id and num_guest to integers:
                try:
                    restaurant_id = int(function_args.get("restaurant_id",0))
                except Exception:
                    restaurant_id = 0
                
                try:
                    num_guests = int(function_args.get("num_guests",0))
                except Exception:
                    num_guests = 0
            
                tool_result = available_functions[function_name](
                    restaurant_id=restaurant_id,
                    location = function_args.get("location",""),
                    name=function_args.get("name",""),
                    date=function_args.get("date",""),
                    time_slot=function_args.get("time_slot",""),
                    num_guests=num_guests,
                    cuisine = function_args.get("cuisine",""),
                    seating = function_args.get("seating",""),
                    RESTAURANTS=RESTAURANTS
                )
            else:
                tool_result = "Tool function not implemented."
                
                
            #Ensure tool result is a string
            if not isinstance(tool_result, str):
                tool_result = str(tool_result)
            
            # Append the tool's response to the conversation as a tool message.
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": tool_result
            })
            
            
            
        # Before the second call, ensure each message's content is a string.
        for m in messages:
            m['content'] = str(m.get('content', ''))
        
        # Make a second API call with the updated conversation history.
        try:
            second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0)
        except Exception:
            return {"response": "Unfortunately, there is a connection issues with the model. Please try after some time."}
        
        final_response = second_response.choices[0].message.content
        try:
            final_result = json.loads(final_response)
            return final_result
        except json.JSONDecodeError:
            #return {"response": final_response}
            return {"intent": "chat", "parameters": {}, "response": final_response}
    else:
        # No tool calls were made, so process the response normally.
        try:
            response_text = response_message.content.strip() if response_message.content else ""
            return json.loads(response_text)
        except json.JSONDecodeError:
            #return {"response": response_message.content or ""}
            return {"intent": "chat", "parameters": {}, "response": response_message.content or ""}
        
        

    # if response and response.choices:
    #     try:
    #         #parse the returnsed json message content
            
    #         response_text = response.choices[0].message.content
            
    #         if response_text:
    #             response_text = response_text.strip()
    #         else:
    #             print(response)
    #             return {"intent": "chat", "parameters": {}, "response": "No content recieved from the endpoint."}
            
    #         api_result = json.loads(response_text)
            
    #     except json.JSONDecodeError:
    #         # if parsing fails,fall back to default
    #         return {"intent":"chat","parameters":{}, "response": response_text}
    #     return api_result
    # else:
    #     return {"intent": "chat", "parameters": {}, "response":"Error reaching the service. I apologize for the inconvenience. Please try again later."}
    
    
    
    #if response.status_code == 200:
    #    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "I couldn't process your request.")
    #else:
    #    return "Error reaching service. Please try again later."
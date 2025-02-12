
from dotenv import load_dotenv
from groq import Groq
import json
from datetime import datetime



#---------------------------------------------GROQCLOUD PART------------------------------------------------------------------
#get the api key 

load_dotenv()

#using the llama-3.1-8b model
MODEL = "llama-3.1-8b-instant"

#init the Groqcloud client
client = Groq()




#---------------------------------------------TOOL PART------------------------------------------------------------------
#Find restaurants based on criteria (help user decide on a restaurant)-TOOL 1

def find_restaurants(criteria: dict, RESTAURANTS: list) -> str:
    """
    Find restaurants that match given criteria.
    Args:
        criteria (dict): A dictionary containing the search criteria. Possible keys are:
            - "cuisine" (str or list of str): The desired cuisine(s).
            - "seating" (str or list of str): The desired seating type(s).
            - "location" (str or list of str): The desired location.(This is optional and not used)
        RESTAURANTS (list): A list of dictionaries, where each dictionary represents a restaurant with keys:
            - "cuisine" (list of str): The cuisines offered by the restaurant.
            - "seating" (list of str): The seating types available at the restaurant.
            - "location" (str): The location of the restaurant.
    Returns:
        str: A formatted string listing the restaurants that match the criteria, or a message indicating no matches were found.
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

        # Process location criteria: if provided as a list, take the first element.(optional)
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
    Parameters:
        restaurant_id (int): The unique identifier of the restaurant.
        location (str): The location of the restaurant.
        name (str): The name of the person making the reservation.
        date (str): The date of the reservation.
        time_slot (str): The time slot for the reservation.
        num_guests (int): The number of guests for the reservation.
        cuisine (str): The type of cuisine preferred.
        seating (str): The seating arrangement preferred.
        RESTAURANTS (list): A list of dictionaries containing restaurant information.
    Returns:
        str: A confirmation message if the reservation is successful, or an error message if the restaurant is not found.
    
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
    - Using available tools, search for restaurants that match the user's specified cuisine and/or seating preferences. If matching restaurants are found, always return them as a bulleted list in the response to make it easier for the user to choose.
    - Then use the restaurant the user chose from the bulleted list for the reservation.
    - Always make reservations by asking the customer's name, reservation date(must be after the date {current_date}), preferred time slot (between 11:00 and 22:00) and guest count.
    - For time slots, accept inputs in either 12-hour (e.g., '5pm') or 24-hour (e.g., '17:00') format. Convert any 12-hour input to 24-hour format to ensure the time falls between 11:00 and 22:00. If the converted time is outside this range, ask the user for a valid time.
    - When requested or after completing a reservation, display existing reservations in a Markdown table with columns: Name, Date, Time Slot, Number of Guests, Restaurant, Seating, and Cuisine. Modify the information in the existing reservations based on the user's preferences.
   

    Rules:
    - Only assist with FoodieSpot reservations; if unrelated, reply: 
      "Unfortunately, I can only assist with FoodieSpot restaurant reservations."
    - Always respond as a JSON object with "intent", "parameters", and "response".
    - "intent" must be "find_restaurant", "make_reservation", or "chat". Do not reference internal function names or tool calls (find_restaurant, make_reservation) in your output.
    - Do not assume or generate missing details; only use what the user provides or retrieved via tools.
    - For every new reservation request, if any essential detail (cuisine, seating, customer's name, date, time slot, or number of guests) is missing, ask the user to provide it. If any detail is already known from previous reservations, ask the user whether to reuse the known value or provide a new one. Always confirm all details with the user before finalizing the reservation.
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
  
   
    



#Define the available tools before calling the model
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
                            "location": {"type": "string", "description": "Restaurant location (optional)"},
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

def call_groq_llama(conversation_history:list, user_message:str,RESTAURANTS:list):
    """
        Handles the interaction with the Groqcloud Llama 3.1-8b model, including processing tool calls if necessary.
        Args:
            conversation_history (list): The history of the conversation as a list of message dictionaries.
            user_message (str): The latest message from the user.
            RESTAURANTS (list): A list of available restaurants and other related information.
        Returns:
            dict: A dictionary containing the intent, parameters, and response message.
        Raises:
            Exception: If there is an error reaching the service or processing the response.
        The function performs the following steps:
        1. Constructs the initial payload with the system prompt, conversation history, and user message.
        2. Makes an API call to the Groq Llama model.
        3. If tool calls are present in the response, processes each tool call by invoking the corresponding function.
        4. Updates the conversation history with the tool responses and makes a second API call.
        5. Returns the final response from the model, either as a parsed JSON object/dict or a plain string.
    """
    
    sys_prompt = [{"role":"system", "content":system_prompt()}]
    messages = sys_prompt + conversation_history + [{"role": "user", "content": user_message}]
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "tools" : tools,
        "tool_choice" : "auto",
        
    }
    
    try:
        response = client.chat.completions.create(**payload)
    except Exception as e:
        return {"intent": "chat", "parameters": {}, "response": "Error reaching the service. I apologize for the inconvenience. Please try again later."}
    
    
    response_message = response.choices[0].message
    
    #if content is None and tool_calls are provided, process tool calls 
    if response_message.content is None and response_message.tool_calls:
    
   
        
        #define a mappig from tool calls names to respective functions
        available_functions = {
            "find_restaurants": find_restaurants,
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
            return {"intent": "chat", "parameters": {}, "response": "Unfortunately, there is a connection issue with the model. Please try again later."}
        
        final_response = second_response.choices[0].message.content
        try:
            final_result = json.loads(final_response)
            
            # Ensure the response contains required keys
            if isinstance(final_result, dict) and "response" in final_result:
                return final_result
            else:
                raise ValueError("Missing keys")
        except json.JSONDecodeError:
           
            return {"intent": "chat", "parameters": {}, "response": final_response}
    else:
        # No tool calls were made, so process the response normally.
        try:
            response_text = response_message.content.strip() if response_message.content else ""
            return json.loads(response_text)
        except json.JSONDecodeError:
            
            return {"intent": "chat", "parameters": {}, "response": response_message.content or ""}
        
        

   
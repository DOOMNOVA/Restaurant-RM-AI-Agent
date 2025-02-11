import random
import streamlit as st
import base64


#Helper function 
def generate_restaurants(n=30) -> list: 
    cuisines = ["Italian", "Chinese", "Indian", "Mexican", "French", "Japanese", "Mediterranean"]
    seating_options = ["indoor", "outdoor", "rooftop", "private"]
    
    #30 locations
    location_names = [
        "MG Road", "Brigade Road", "Connaught Place", "Marine Drive", "Park Street",
        "Banjara Hills", "Residency Road", "Linking Road", "Anna Salai", "Rajpath",
        "Camac Street", "Commercial Street", "Shivaji Nagar", "Church Street", "Law Garden",
        "FC Road", "New Market", "DLF Cyber Hub", "Hauz Khas", "Sector 17",
        "Karol Bagh", "Saket", "Juhu Beach Road", "Lal Bagh", "Electronic City",
        "T Nagar", "Gariahat", "Koregaon Park", "Powai", "Indiranagar"
    ]
    #locations = random.sample(location_names,n_locations =30)
    restaurants = []
    for i, loc in enumerate(location_names):
        restaurant = {
            "id": i+1,
            #"name": f"FoodieSpot, {loc}",
            "location": f"FoodieSpot - {loc}",
            "cuisine": random.sample(cuisines, k=random.randint(1, 3)),
            "seating": random.sample(seating_options, k=random.randint(1, 3))
        }
        restaurants.append(restaurant)
    
    return restaurants



# encode image in base64 and add it to the background using CSS

def add_bg_image(img_file):
    with open(img_file,"rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
            url("data:image/jpg;base64,{encoded}");
            background-size: contain;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center center;
        }}
        </style>
        """,
     unsafe_allow_html=True   
    )
            
            
            
            
            
# Inject custom CSS to style the background and chat area
def apply_chatbot_styles(background_image_url: str):
    """
    Applies CSS styling to Streamlit for a chatbot UI.
    
    - Sets a background image for the entire app.
    - Creates a black background for the chat area.
    - Styles user and bot messages for better readability.

    Args:
    background_image_url (str): URL or path to the background image.
    """
    st.markdown(
        f"""
        <style>
        /* Set full-page background image */
        .stApp {{
            background: url("{background_image_url}") no-repeat center center fixed;
            background-size: cover;
        }}
        
        /* Black background for chat container */
        .chat-container {{
            background-color: black;
            padding: 15px;
            border-radius: 10px;
            color: white;
            max-width: 80%;
            margin: auto;
            box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.3);
        }}
        
        /* Style user messages */
        .user-message {{
            background-color: #333;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            color: white;
        }}
        
        /* Style bot messages */
        .bot-message {{
            background-color: #444;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    
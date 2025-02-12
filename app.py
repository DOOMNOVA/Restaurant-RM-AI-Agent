import streamlit as st
from datetime import datetime
from src.utils_data.restaurant_data import add_bg_image,generate_restaurants
from src.model.agent import call_groq_llama


def main():
    """
    Main function to run the FoodieSpot Reservation Chatbot application.
    This function sets up the Streamlit page configuration, initializes the conversation history,
    displays the chat interface, and handles user input for restaurant selection and messaging.
    Key functionalities:
    - Sets the page title and icon.
    - Displays the title and background image.
    - Generates a list of FoodieSpot restaurants with varying cuisines, locations, and seating options.
    - Initializes the conversation history in the session state.
    - Displays the chat history between the user and the assistant.
    - Provides a form for user input, including cuisine and seating selection.
    - Handles form submission, updates the conversation history, and calls the GroqCloud API to process user input.
    - Displays the assistant's response and reruns the app to update the conversation.
    Note: This function relies on external functions such as `add_bg_image`, `generate_restaurants`, and `call_groq_llama`.
    """
    
    st.set_page_config(page_title="FoodieSpot Chatbot",page_icon="🍽️")
    st.title("FoodieSpot Reservation Chatbot")
    
    #add background image for the app
    add_bg_image("images/FoodieSpot.jpg")
    

    
    #Generate 30 FoodieSpot restaurants with varying cuisines,locations and seating options
    RESTAURANTS = generate_restaurants()
    unique_cuisines = sorted({c for restaurant in RESTAURANTS for c in restaurant["cuisine"]})
    unique_seating = sorted({s for restaurant in RESTAURANTS for s in restaurant["seating"]})

    #Initialize conversation history in session state.
    if "conversation" not in st.session_state:
        st.session_state.conversation=[{
            "sender": "FoodieSpot",
            "message" :"Welcome to FoodieSpot Reservations! I'm FoodieBot—your assistant for finding restaurants and booking tables. You can either chat with me or use the dropdown options. How can I help?"
        }]
        
        
    st.subheader("Chat")
    
   
    
    for entry in st.session_state.conversation:
        if entry["sender"]=="user":
            st.markdown(f"**YOU👤:** {entry['message']}")
        else:
            st.markdown(f"**FoodieSpot 🤖:** {entry['message']}")

            
            

    
            
    #User input form with drop down selection for cuisine and seating preference.
    with st.form(key="chat_form", clear_on_submit=True):
        
        
        selected_cuisine = st.selectbox("Select Cuisine", ["None"] + unique_cuisines)
        selected_seating = st.selectbox("Select Seating", ["None"] + unique_seating)
        user_input = st.text_input("Your message:")
        submit_button = st.form_submit_button(label="Send")
        
    
    if submit_button:
        #add the user message to conversation history
        combined_input = user_input.strip()
        
        if selected_cuisine not in ["None", "", None]:
            combined_input += f". Selected Cuisine: {selected_cuisine}"
           
        if selected_seating not in ["None", "", None]:
            combined_input += f". Selected Seating: {selected_seating}"
          
         
        print("input:", combined_input)
        
        
        st.session_state.conversation.append({"sender":"user","message":combined_input})
        
        #build conversation history with both user and assistant messages
        conversation_history = [{"role": "user" if entry["sender"] == "user" else "assistant", "content": entry["message"]} for entry in st.session_state.conversation]

    
        #call groqcloud API to decide intent
        api_result = call_groq_llama(conversation_history=conversation_history, user_message= combined_input, RESTAURANTS=RESTAURANTS)
        
        #use the final response provided by the function
        final_response = api_result.get("response", "I'm not sure how to handle that request. Can you please clarify? I am happy to help you find a restaurant or make a reservation.")
        
        
    
        st.session_state.conversation.append({"sender":"assistant","message":final_response})

        #rerun to show the updated conversation.
        st.rerun()            
            
        
    
if __name__ == "__main__":
    main()







        

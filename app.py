import streamlit as st
from datetime import datetime
from src.utils_data.restaurant_data import add_bg_image,generate_restaurants
from src.model.agent import call_groq_llama


def main():
    
    st.set_page_config(page_title="FoodieSpot Chatbot",page_icon="🍽️")
    st.title("FoodieSpot Reservation Chatbot")
    
    #add background image for the app
    #add_bg_image("images/FoodieSpot.jpg")
    
#custom css for green chat text
    # st.markdown(
    #     """
    #     <style>
    #         .matrix-green {
    #             color: #00FF00;
    #             font-family: monospace;
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )    
    
    
    
    
    #Generate 30 FoodieSpot restaurants with varying cuisines,locations and seating options
    RESTAURANTS = generate_restaurants()
    restaurant_options = {f"{r['location']}": r['id'] for r in RESTAURANTS}
    unique_cuisines = sorted({c for restaurant in RESTAURANTS for c in restaurant["cuisine"]})
    unique_seating = sorted({s for restaurant in RESTAURANTS for s in restaurant["seating"]})

    #Initialize conversation history in session state.
    if "conversation" not in st.session_state:
        st.session_state.conversation=[{
            "sender": "FoodieSpot",
            "message" :"Welcome to FoodieSpot Reservations! I'm FoodieBot—your assistant for finding restaurants and booking tables. You can either chat with me or use the dropdown options. How can I help?"
        }]
        
        
    st.subheader("Chat")
    
    #black chat background container
    #st.markdown('<div class="chat-container">',unsafe_allow_html=True)
    
    
    
    
    for entry in st.session_state.conversation:
        if entry["sender"]=="user":
            st.markdown(f"**YOU👤:** {entry['message']}")
        else:
            st.markdown(f"**FoodieSpot 🤖:** {entry['message']}")

            
            
    #st.markdown("</div>",unsafe_allow_html=True)
    
            
    #User input form with drop down selection
    with st.form(key="chat_form", clear_on_submit=True):
        
        # = st.selectbox("Or Select a restaurant:", ["None"] + list(restaurant_options.keys()))
        #  # --- Restaurant selection (outside the form) ---
        # selected_restaurant = st.selectbox("Select a restaurant:", ["None"] + list(restaurant_options.keys()), key="selected_restaurant")
    
        # # Based on the selected restaurant, update cuisine and seating options.
        # if selected_restaurant != "None":
        #     # Find the restaurant object that matches the selected location.
        #     rest_obj = next((r for r in RESTAURANTS if r["location"] == selected_restaurant), None)
        #     if rest_obj:
        #         cuisine_options = ["None"] + rest_obj["cuisine"]
        #         seating_options = ["None"] + rest_obj["seating"]
        #     else:
        #         cuisine_options = ["None"] + unique_cuisines
        #         seating_options = ["None"] + unique_seating
        # else:
        #     cuisine_options = ["None"] + unique_cuisines
        #     seating_options = ["None"] + unique_seating
                
        
        
        selected_cuisine = st.selectbox("Select Cuisine", ["None"] + unique_cuisines)
        selected_seating = st.selectbox("Select Seating", ["None"] + unique_seating)
        user_input = st.text_input("Your message:")
        submit_button = st.form_submit_button(label="Send")
        
    
    if submit_button:
        #add the user message to conversation history
        combined_input = user_input.strip()
        
        # if selected_restaurant not in ["None", "", None]:
        #     combined_input += f" Selected Location: {selected_restaurant}"
         
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







        

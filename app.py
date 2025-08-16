
import streamlit as st
import google.generativeai as genai

# Replace with your actual API key from Google AI Studio
GEMINI_API_KEY = "AIzaSyDeCMSLXBbcE26AcukVVEkhoeEouUehQrk"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model (use 'gemini-1.5-flash' for speed/cost)
model = genai.GenerativeModel('gemini-1.5-flash')

# App title and description
st.title("Hyper-Personalized Travel Planner")
st.markdown("""
Welcome! I'm your AI planner specializing in family trips to theme parks or scenic destinations like Shimla. 
I'll ask questions to customize your itinerary. All costs are in Indian Rupees (INR). Let's start chatting!
""")

# Sidebar for user settings (beautiful and interactive)
with st.sidebar:
    st.header("Trip Settings")
    niche = st.selectbox("Travel Niche", ["Family Trips to Theme Parks", "Family Trips to Hill Stations"])  # Added Shimla-friendly option
    destination = st.text_input("Destination (e.g., Shimla)", "Shimla")
    trip_length = st.slider("Trip Length (days)", 1, 14, 5)
    budget = st.number_input("Approximate Budget (₹ per person)", min_value=1000, max_value=100000, value=30000, step=1000)
    st.info("Chat below to refine and generate your itinerary.")

# Initialize chat history and profile in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}  # Store user preferences

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Tell me about your trip or answer my questions...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate AI response using Gemini
    with st.chat_message("assistant"):
        # Build conversation history
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        prompt = f"""
        You are a hyper-personalized travel planner for {niche} trips to {destination}.
        User's budget: ₹{budget} per person for {trip_length} days.
        
        Build a profile by asking 1-2 questions at a time (e.g., 'Are you a night owl or early riser?', 'Group size and ages?', 'Preferences: fast-paced or relaxed?').
        Once you have enough info (after 3-5 exchanges), generate a full minute-by-minute itinerary including:
        - Flights/trains (mock for now, e.g., 'Train from Delhi to Shimla: ₹4000').
        - Hotels, activities, dining, transport.
        - Cost breakdown in INR.
        - Allow modifications.
        
        Conversation history: {history}
        Respond conversationally and helpfully.
        """
        
        # Call Gemini
        try:
            response = model.generate_content(prompt)
            ai_response = response.text
        except Exception as e:
            ai_response = f"Error with Gemini API: {str(e)}. Please check your API key or try again."
        
        # Display response
        st.markdown(ai_response)
        
        # Add to history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # Update profile (simple parsing for demo)
        if "early riser" in user_input.lower():
            st.session_state.profile["schedule"] = "Early riser"
        if "group size" in user_input.lower() or "family" in user_input.lower():
            st.session_state.profile["group_size"] = user_input.lower()  # Simplified; parse as needed

# Button to generate full itinerary (if ready)
if st.button("Generate Full Itinerary (if ready)"):
    with st.spinner("Crafting your perfect trip..."):
        # Redefine history for this scope
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        # Final prompt for itinerary
        profile_str = "\n".join([f"{k}: {v}" for k, v in st.session_state.profile.items()])
        final_prompt = f"""
        Based on this profile: {profile_str}
        And conversation history: {history}
        Generate a detailed, minute-by-minute itinerary for a {trip_length}-day {niche} trip to {destination}.
        Use this default profile if not fully specified:
        - Family of 4 (2 adults, 2 children aged 8 and 10), starting from Delhi, early risers, prefer relaxed pace with scenic views, light adventure, and vegetarian meals.
        Include:
        - Day-by-day breakdown.
        - Estimated costs in INR (total under ₹{budget * (len(st.session_state.profile.get('group_size', [1, 1, 1, 1])) or 4)} for family).
        - Mock bookings: trains, hotels, activities, dining, transport.
        Format beautifully with markdown tables.
        """
        try:
            response = model.generate_content(final_prompt)
            st.markdown("### Your Customized Itinerary")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Failed to generate itinerary: {str(e)}. Please ensure enough profile data or check API key.")

# Footer for beauty
st.markdown("---")
st.caption("Powered by Google Gemini. All costs in INR. Feedback? Share with your travel community!")
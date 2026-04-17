import streamlit as st
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import os
import re
import socket

def _get_local_ip():
    """Detect the machine's LAN IP address automatically."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(page_title="Passport Rank Predictor", layout="centered")

# ============================================================================
# TITLE AND DESCRIPTION
# ============================================================================
st.title("🛂 Passport Rank Predictor")
st.markdown("Predict passport rank based on visa-free access count")

_local_ip = _get_local_ip()
st.info(f"🌐 App accessible at: http://localhost:8501  |  http://{_local_ip}:8501")

# ============================================================================
# LOAD DATA AND TRAIN MODEL (cached for performance)
# ============================================================================
@st.cache_resource
def load_and_train_model():
    """Load data and train the DecisionTreeRegressor model"""
    # Load the raw dataset (has the rank data we need)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base_dir, 'countries_visa_free_access.csv'))
    
    # Extract numeric rank from ordinal strings (e.g., "1st" -> 1, "2nd" -> 2)
    def extract_rank_number(rank_str):
        match = re.search(r'\d+', str(rank_str))
        return int(match.group()) if match else None
    
    df['Rank_Numeric'] = df['Rank'].apply(extract_rank_number)
    
    # Prepare features and target
    X = df[['Visa-Free Access']].rename(columns={'Visa-Free Access': 'visa_free_access'})
    y = df['Rank_Numeric']
    
    # Train the model
    model = DecisionTreeRegressor(random_state=42)
    model.fit(X, y)

    # Compute MSE on a holdout set for quick model quality feedback
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    eval_model = DecisionTreeRegressor(random_state=42)
    eval_model.fit(X_train, y_train)
    y_pred = eval_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    
    return model, df, mse

# Load model and data
model, df, mse_value = load_and_train_model()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_country_by_rank(rank_numeric):
    """Find countries that have a specific numeric rank"""
    # Round to nearest integer for matching
    rank_int = round(rank_numeric)
    
    # Convert Rank column to numeric
    df['Rank_Numeric'] = df['Rank'].apply(lambda x: int(re.search(r'\d+', str(x)).group()) if re.search(r'\d+', str(x)) else None)
    
    # Find matching countries
    matching = df[df['Rank_Numeric'] == rank_int]
    
    if len(matching) > 0:
        countries = matching['Country'].tolist()
        return countries
    return None

def generate_suggestion(visa_free_access):
    """Generate a comment/suggestion based on visa-free access count"""
    if visa_free_access >= 190:
        return "🌟 Excellent! This is a very strong passport with access to most countries!"
    elif visa_free_access >= 180:
        return "✨ Great! This passport offers extensive travel freedom to most regions."
    elif visa_free_access >= 170:
        return "👍 Good! This passport provides solid global travel access."
    elif visa_free_access >= 150:
        return "📍 Decent access. This passport covers major travel destinations."
    elif visa_free_access >= 120:
        return "⚠️ Moderate access. This passport works for many countries but has some limits."
    elif visa_free_access >= 100:
        return "🛂 Basic access. More destinations require visa applications."
    else:
        return "📋 Limited access. This passport requires visas for most international travel."

# ============================================================================
# INITIALIZE SESSION STATE FOR CHAT HISTORY
# ============================================================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ============================================================================
# INPUT SECTION
# ============================================================================
st.markdown("---")
st.subheader("Make a Prediction")

col1, col2 = st.columns([3, 1])

with col1:
    visa_input = st.number_input(
        "Enter visa-free access count:",
        min_value=0,
        max_value=200,
        value=100,
        step=1
    )

with col2:
    predict_button = st.button("Predict", use_container_width=True)

# ============================================================================
# MAKE PREDICTION AND UPDATE CHAT HISTORY
# ============================================================================
if predict_button:
    # Make prediction using the model
    prediction_df = pd.DataFrame({'visa_free_access': [visa_input]})
    predicted_rank = model.predict(prediction_df)[0]
    
    # Get country for this rank
    countries = get_country_by_rank(predicted_rank)
    
    # Generate suggestion
    suggestion = generate_suggestion(visa_input)
    
    # Add to chat history
    st.session_state.chat_history.append({
        'visa_free_access': visa_input,
        'predicted_rank': predicted_rank,
        'countries': countries,
        'suggestion': suggestion
    })

# ============================================================================
# DISPLAY CHAT HISTORY
# ============================================================================
st.markdown("---")
st.subheader("Prediction History")

if st.session_state.chat_history:
    for i, entry in enumerate(st.session_state.chat_history, 1):
        with st.container():
            st.markdown(f"**Query {i}:**")
            
            # Display visa-free access and predicted rank
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Visa-Free Access", entry['visa_free_access'])
            with col2:
                st.metric("Predicted Rank", f"{entry['predicted_rank']:.1f}")
            
            # Display country
            if entry['countries']:
                countries_str = ", ".join(entry['countries'])
                st.markdown(f"**🌍 Country Example:** {countries_str}")
            
            # Display suggestion
            st.info(entry['suggestion'])
            
            st.markdown("---")
else:
    st.info("No predictions yet. Enter a value and click Predict to get started!")

# ============================================================================
# CLEAR HISTORY BUTTON
# ============================================================================
if st.session_state.chat_history:
    if st.button("Clear History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ============================================================================
# DATASET INFORMATION
# ============================================================================
st.markdown("---")
with st.expander("📊 Dataset Information"):
    st.write(f"Total countries: {len(df)}")
    st.write(f"Visa-free access range: {df['Visa-Free Access'].min()} - {df['Visa-Free Access'].max()}")
    st.write(f"Rank range: 1 to {int(df['Rank_Numeric'].max())}")
    st.write(f"Model Mean Squared Error (MSE): {mse_value:.4f}")

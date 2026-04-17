import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
import warnings
import argparse
import os

# Suppress scikit-learn warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)

parser = argparse.ArgumentParser(description="Passport rank predictor and MSE evaluator")
parser.add_argument("--mse-only", action="store_true", help="Print only Mean Squared Error and exit")
args = parser.parse_args()

# ============================================================================
# 1. Load the CSV files
# ============================================================================
# Load the raw dataset
base_dir = os.path.dirname(os.path.abspath(__file__))
df_raw = pd.read_csv(os.path.join(base_dir, 'countries_visa_free_access.csv'))

# Load the cleaned dataset
df_cleaned = pd.read_csv(os.path.join(base_dir, 'countries_visa_free_access_cleaned.csv'))

print("Raw dataset shape:", df_raw.shape)
print("Cleaned dataset shape:", df_cleaned.shape)

# ============================================================================
# 2. Prepare the data for modeling
# ============================================================================
# Use raw dataset since it has the rank data
# Extract numeric rank from ordinal strings (e.g., "1st" -> 1, "2nd" -> 2)
import re
def extract_rank_number(rank_str):
    """Extract numeric value from ordinal rank strings like '1st', '2nd', etc."""
    match = re.search(r'\d+', str(rank_str))
    return int(match.group()) if match else None

df_raw['Rank_Numeric'] = df_raw['Rank'].apply(extract_rank_number)

# Prepare feature and target
X = df_raw[['Visa-Free Access']].rename(columns={'Visa-Free Access': 'visa_free_access'})
y = df_raw['Rank_Numeric']

print(f"\nFeature (visa_free_access) shape: {X.shape}")
print(f"Target (rank) shape: {y.shape}")

# ============================================================================
# 3. Split the data into training (80%) and testing (20%) sets
# ============================================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training set size: {len(X_train)}")
print(f"Testing set size: {len(X_test)}")

# ============================================================================
# 4. Train the Decision Tree Regression model
# ============================================================================
model = DecisionTreeRegressor(random_state=42)
model.fit(X_train, y_train)

print("\nDecision Tree model trained successfully!")

# ============================================================================
# 5. Evaluate the model using Mean Squared Error
# ============================================================================
# Make predictions on the test set
y_pred = model.predict(X_test)

# Calculate Mean Squared Error
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error (MSE) on test set: {mse:.4f}")

if args.mse_only:
    print(f"MSE={mse:.4f}")
    raise SystemExit(0)

# ============================================================================
# 6. Interactive CLI prediction loop
# ============================================================================
print("\n" + "="*70)
print("PASSPORT RANK PREDICTOR - Interactive Mode")
print("="*70)
print("Enter a visa-free access number to predict its passport rank.")
print("Type 'exit' to quit the program.\n")

while True:
    # Get user input
    user_input = input("Enter visa-free access number (or 'exit'): ").strip()
    
    # Check if user wants to exit
    if user_input.lower() == 'exit':
        print("\nThank you for using the Passport Rank Predictor. Goodbye!")
        break
    
    # Try to convert input to float
    try:
        visa_free_number = float(user_input)
        
        # Make prediction using DataFrame for consistent feature naming
        prediction_df = pd.DataFrame({'visa_free_access': [visa_free_number]})
        predicted_rank = model.predict(prediction_df)[0]
        
        # Display result
        print(f"  → Predicted rank for {visa_free_number} visa-free access: {predicted_rank:.2f}\n")
        
    except ValueError:
        print("  ✗ Invalid input. Please enter a valid number or 'exit'.\n")

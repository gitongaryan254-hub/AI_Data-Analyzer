import pandas as pd
import matplotlib.pyplot as plt
import os

# Load cleaned data
base_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(base_dir, "countries_visa_free_access_cleaned.csv"))

# Ensure rank is numeric
df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
df["visa_free_access"] = pd.to_numeric(df["visa_free_access"], errors="coerce")

# Drop invalid rows
df = df.dropna(subset=["country", "rank", "visa_free_access"])

# Select top 10 strongest passports
df = df.sort_values("rank", ascending=True).head(10)

# Create bar chart
plt.figure(figsize=(10, 6))
plt.bar(df["country"], df["visa_free_access"], color="steelblue")

# Labels and title
plt.xlabel("Country")
plt.ylabel("Visa-Free Access")
plt.title("Top 10 Strongest Passports by Visa-Free Access")

# Improve readability
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(base_dir, "top10_passport_rank_bar_chart.png"))
print("✅ Bar chart generated successfully")
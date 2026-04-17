import pandas as pd
import os

print("🚀 Starting basic profiling (offline mode)...")

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
input_csv = os.path.join(base_dir, "countries_visa_free_access_cleaned.csv")
output_html = os.path.join(base_dir, "countries_visa_free_access_basic_profile.html")

# Load cleaned CSV
if not os.path.exists(input_csv):
    raise FileNotFoundError("❌ Cleaned CSV not found")

df = pd.read_csv(input_csv)

print("✅ CSV loaded")

# Create profiling content
html_content = f"""
<html>
<head>
    <title>CSV Profiling Report</title>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        h1, h2 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; }}
        th {{ background-color: #f4f4f4; }}
    </style>
</head>
<body>

<h1>Countries Visa-Free Access – Basic Profiling Report</h1>

<h2>Dataset Shape</h2>
<p>Rows: {df.shape[0]}<br>Columns: {df.shape[1]}</p>

<h2>Column Names</h2>
<ul>
    {''.join(f"<li>{col}</li>" for col in df.columns)}
</ul>

<h2>Data Types</h2>
{df.dtypes.to_frame('Type').to_html()}

<h2>Missing Values</h2>
{df.isna().sum().to_frame('Missing Count').to_html()}

<h2>Summary Statistics</h2>
{df.describe(include='all').to_html()}

<h2>Sample Data (First 10 Rows)</h2>
{df.head(10).to_html(index=False)}

</body>
</html>
"""

# Save HTML file
with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ BASIC PROFILING COMPLETE!")
print(f"📄 HTML report saved at:\n{output_html}")
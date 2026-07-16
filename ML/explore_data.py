import pandas as pd

df = pd.read_csv("data/mental_health.csv")

# Drop the unnamed index column and rows with missing text
df = df.drop(columns=["Unnamed: 0"])
df = df.dropna(subset=["statement"])

# Map the 7 raw categories into 3 risk levels
risk_map = {
    "Normal": "low",
    "Anxiety": "moderate",
    "Stress": "moderate",
    "Bipolar": "moderate",
    "Personality disorder": "moderate",
    "Depression": "high",
    "Suicidal": "high",
}
df["risk_level"] = df["status"].map(risk_map)

print("Shape after cleaning:", df.shape)
print("\nRisk level distribution:")
print(df["risk_level"].value_counts())

# Save the cleaned version so we don't repeat this step every time
df.to_csv("data/cleaned_mental_health.csv", index=False)
print("\nSaved cleaned_mental_health.csv")
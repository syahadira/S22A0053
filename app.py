import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns # Ensure seaborn is imported for histplot and countplot

# --- 1. Data Loading and Preparation ---

url = "https://raw.githubusercontent.com/syahadira/S22A0053/refs/heads/main/arts_faculty_data.csv"
response = requests.get(url)

# Save the content to a local CSV file
# This step is often necessary when working outside of environments like Colab/Jupyter where direct URL reading might be preferred
with open("arts_faculty_data.csv", "wb") as f:
    f.write(response.content)

# Read the CSV into a pandas DataFrame
arts_faculty_df = pd.read_csv("arts_faculty_data.csv")

# Display the first 5 rows to verify (In a console environment, you'd use print)
print("--- Data Head ---")
print(arts_faculty_df.head())
print("-" * 20)

# --- 2. Visualizations (7 Plots) ---

# Get gender counts for pie/bar charts
gender_counts = arts_faculty_df['Gender'].value_counts()


# 1. Gender Distribution (Pie Chart)
plt.figure(figsize=(6, 6))
plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Gender Distribution in Arts Faculty (Pie Chart)')
plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()


# 2. Gender Distribution (Bar Chart)
plt.figure(figsize=(8, 6))
plt.bar(gender_counts.index, gender_counts.values)
plt.title('Gender Distribution in Arts Faculty (Bar Chart)')
plt.xlabel('Gender')
plt.ylabel('Count')
plt.show()


# 3. Arts Program Distribution
plt.figure(figsize=(10, 6))
sns.countplot(data=arts_faculty_df, x='Arts Program')
plt.title('Distribution of Arts Programs')
plt.xlabel('Arts Program')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# 4. Distribution of S.S.C (GPA)
plt.figure(figsize=(8, 6))
sns.histplot(data=arts_faculty_df, x='S.S.C (GPA)', kde=True)
plt.title('Distribution of S.S.C (GPA)')
plt.xlabel('S.S.C (GPA)')
plt.ylabel('Frequency')
plt.show()


# 5. Distribution of H.S.C (GPA)
plt.figure(figsize=(8, 6))
sns.histplot(data=arts_faculty_df, x='H.S.C (GPA)', kde=True)
plt.title('Distribution of H.S.C (GPA)')
plt.xlabel('H.S.C (GPA)')
plt.ylabel('Frequency')
plt.show()


# 6. Relationship between Classes are mostly and Gender
plt.figure(figsize=(10, 6))
sns.countplot(data=arts_faculty_df, x='Classes are mostly', hue='Gender')
plt.title('Distribution of Class Modality by Gender')
plt.xlabel('Class Modality')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# 7. Classes are mostly Distribution (Overall Modality)
plt.figure(figsize=(8, 6))
sns.countplot(data=arts_faculty_df, x='Classes are mostly')
plt.title('Distribution of Class Modality (Overall)')
plt.xlabel('Class Modality')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


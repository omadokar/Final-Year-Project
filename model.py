import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ========================
# MySQL DB Configuration
# ========================
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'omadokar',
    'database': 'user_data'
}

# ========================
# Connect to MySQL
# ========================
try:
    connection = mysql.connector.connect(**db_config)
    print("Connected to MySQL database.")
except mysql.connector.Error as e:
    print(f"Error: {e}")
    exit()

# ========================
# 1. Career Prediction Distribution
# ========================
query = "SELECT career_prediction FROM career_history"
df = pd.read_sql(query, connection)

plt.figure(figsize=(10, 6))
sns.countplot(data=df, x="career_prediction", palette="coolwarm")
plt.title("Distribution of Predicted Careers")
plt.xlabel("Career")
plt.ylabel("Number of Users")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("career_prediction_distribution.png")
plt.show()

# ========================
# 2. Accuracy Comparison (Traditional vs ML)
# ========================
methods = ['Traditional Aptitude Test', 'NextGen ML Model']
accuracy = [65, 88]  # Use real accuracy if available

plt.figure(figsize=(6, 4))
sns.barplot(x=methods, y=accuracy, palette='Set2')
plt.ylim(0, 100)
plt.title('Accuracy Comparison')
plt.ylabel('Accuracy (%)')
plt.tight_layout()
plt.savefig("accuracy_comparison.png")
plt.show()

# ========================
# 3. User Satisfaction Histogram (Optional)
# ========================
# Replace with real feedback if stored
feedback_scores = [5, 4, 5, 3, 4, 4, 5, 3, 5, 4]

plt.figure(figsize=(6, 4))
sns.histplot(feedback_scores, bins=5, kde=True, color='skyblue')
plt.title("User Satisfaction Ratings")
plt.xlabel("Rating (1 to 5)")
plt.ylabel("Number of Users")
plt.tight_layout()
plt.savefig("user_satisfaction.png")
plt.show()

# ========================
# Close DB connection
# ========================
connection.close()
print("Graph generation complete. PNG files saved.")

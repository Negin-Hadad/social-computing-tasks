# python -m pip install pandas
import sqlite3
import pandas
import matplotlib.pyplot as plt

DB_FILE = r"e:\OuluUni\period1\SocialComputing\Homeworks\database.sqlite"
 
try:
    conn = sqlite3.connect(DB_FILE)
    users = pandas.read_sql_query("SELECT * FROM users", conn)
    posts = pandas.read_sql_query("SELECT * FROM posts", conn)
    comments = pandas.read_sql_query("SELECT * FROM comments", conn)
    reactions = pandas.read_sql_query("SELECT * FROM reactions", conn)
except Exception as e:
    print(f"Uh oh '{e}'")
finally:
    if conn:
        conn.close()
        print("SQLite Database connection closed.")

# Task 2.1
allPostsDates = posts['created_at'].str[:7].reset_index(name='month')
allCommentsDates = comments['created_at'].str[:7].reset_index(name='month')
allActivityDates = pandas.concat([allPostsDates, allCommentsDates])
countPerMonth = allActivityDates.groupby('month').size()
monthlyCounts = countPerMonth.reset_index(name='monthly_activity').sort_values('month')
monthlyCounts['cumulative_activity'] = monthlyCounts['monthly_activity'].cumsum()
print("Monthly and Cumulative Activity of The Platform:")
print(monthlyCounts)

# Plot
plt.plot(monthlyCounts['month'], monthlyCounts['cumulative_activity'])
plt.title("Cumulative activity/Load on Platform Over Time")
plt.xlabel("Month")
plt.ylabel("Total Cumulative activity/Load")
plt.xticks(rotation=60)
plt.grid(True)
plt.show()

# Naive growth estimate
currentTotal = monthlyCounts['cumulative_activity'].iloc[-1]
print(f"\nCurrent total activity = {currentTotal}")
nMonths = len(monthlyCounts)
avgGrowth = currentTotal / nMonths
print(f"Average growth per month = {avgGrowth}")
futureTotal = currentTotal + 36*avgGrowth
print(f"Predicted total after 36 months = {futureTotal}")
activityPerServer = currentTotal / 16
requiredServers = futureTotal / activityPerServer
print(f"\nServers required (no redundancy) = {round(requiredServers)}")
requiredServersWithRedundancy = requiredServers * 1.2
print(f"Servers required (with 20% redundancy) = {round(requiredServersWithRedundancy)}")
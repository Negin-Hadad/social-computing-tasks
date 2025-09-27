# python -m pip install pandas
import sqlite3
import pandas
import matplotlib.pyplot as plt
import numpy as np

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

# Task 2.2
commentsCount = comments.groupby("post_id").size().reset_index(name="comment_count")
reactionsCount = reactions.groupby("post_id").size().reset_index(name="reaction_count")

mergedCounts = pandas.merge(commentsCount, reactionsCount, on="post_id", how="outer").fillna(0)
mergedCounts['total_count'] = (mergedCounts['comment_count'] + mergedCounts['reaction_count'])
mergedCountsSorted = mergedCounts.sort_values("total_count", ascending= False).reset_index(drop=True)

viralPosts = mergedCountsSorted.head(3)
print(f"Three Viral Posts(MAX(comments + reactions)):")
print(viralPosts)

result =[]
for viralPostId in viralPosts['post_id']:
    result.append(posts[posts['id']==viralPostId])
print(result)

# Task 2.3
minCommentDate = comments.groupby("post_id")["created_at"].min().reset_index().rename(columns={"created_at": "min_comment_created_at", "post_id": "id"})
mergedDates = pandas.merge(posts, minCommentDate, on="id", how="right")
mergedDates["min_duration"] = pandas.to_datetime(mergedDates['min_comment_created_at']) - pandas.to_datetime(mergedDates['created_at'])
mergedDates["min_duration"] = mergedDates["min_duration"].dt.total_seconds()/ 3600 # convert to hours
minDurationAverage = mergedDates["min_duration"].mean()
print(f"The average of minimum duration of a post's engagement: {minDurationAverage} hours")

maxCommentDate = comments.groupby("post_id")["created_at"].max().reset_index().rename(columns={"created_at": "max_comment_created_at", "post_id": "id"})
mergedDates = pandas.merge(posts, maxCommentDate, on="id", how="right")
mergedDates["max_duration"] = pandas.to_datetime(mergedDates['max_comment_created_at']) - pandas.to_datetime(mergedDates['created_at'])
mergedDates["max_duration"] = mergedDates["max_duration"].dt.total_seconds()/ 3600 # convert to hours
maxDurationAverage = mergedDates["max_duration"].mean()
print(f"The average of maximum duration of a post's engagement: {maxDurationAverage} hours")

# Task 2.4
engagements = pandas.concat([comments[["user_id","post_id"]], reactions[["user_id","post_id"]]], ignore_index=True).rename(columns={"user_id":"viewer_user_id"})
posts = posts[["id", "user_id"]].rename(columns={"id": "post_id"})
mergedWithPost = pandas.merge(engagements,posts, on="post_id", how="left").dropna()
mergedWithPost["user_pair_id"] = list(zip(np.minimum(mergedWithPost["viewer_user_id"], mergedWithPost["user_id"]), np.maximum(mergedWithPost["viewer_user_id"], mergedWithPost["user_id"])))
engagementCounts = mergedWithPost.groupby("user_pair_id", as_index=False)["post_id"].count().rename(columns={"post_id": "post_count"}).sort_values("post_count", ascending=False)
topThreePairs = engagementCounts.head(3)
print(topThreePairs)
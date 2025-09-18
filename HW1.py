# pip install pandas
import sqlite3
import pandas as pd

DB_FILE = r"e:\OuluUni\period1\SocialComputing\assignments\database.sqlite"

try:
    conn = sqlite3.connect(DB_FILE)
    print("SQLite DB connection successful")
except Exception as e:
    print(f"Error in connecting to DB: '{e}'")

# Task 1.1
tableNames_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(f'table names:\n {tableNames_df}')

for table in ['users', 'posts', 'comments', 'reactions', 'follows']:
    tableContent = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    print(f'\nTable "{table}" number of rows: {len(tableContent)}')
    print(f'\nTable "{table}" columns description:')
    columns = pd.read_sql_query(f"PRAGMA table_info({table})", conn)
    print(columns[["name", "type"]])
    print("-------------------------------")
    
# Task 1.2
try:
    notReactedOrPostedUsers = pd.read_sql_query("""
        SELECT id FROM users WHERE users.id NOT IN
            (SELECT DISTINCT(reactions.user_id) FROM reactions
            UNION
            SELECT DISTINCT(posts.user_id) FROM posts);
        """, conn)
    print(len(notReactedOrPostedUsers))
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    
# Task 1.3
try:
    reactionNumbersBasedOnPostId = pd.read_sql_query("""
        SELECT posts.id As post_id, posts.user_id, COUNT(reactions.id) AS reactions_count
        FROM posts 
        LEFT JOIN reactions ON posts.id = reactions.post_id
        GROUP BY posts.id
        ORDER BY reactions_count;                                             
    """, conn)
    commentNumbersBasedOnPostId = pd.read_sql_query("""
        SELECT posts.id As post_id, posts.user_id, COUNT(comments.id) AS comments_count
        FROM posts 
        LEFT JOIN comments ON posts.id = comments.post_id
        GROUP BY posts.id
        ORDER BY comments_count;                                             
    """, conn)
    totalEngagementOfPosts = pd.merge(reactionNumbersBasedOnPostId, commentNumbersBasedOnPostId, on=['post_id','user_id'])
    totalEngagementOfPosts['engagement_count'] = totalEngagementOfPosts['reactions_count'] + totalEngagementOfPosts['comments_count']
    totalEngagementOfUsers = (totalEngagementOfPosts.groupby('user_id')['engagement_count'].sum().reset_index().sort_values('engagement_count',ascending=False)).head()
    
    influencer = []
    for userId in totalEngagementOfUsers['user_id']:
       influencer.append(pd.read_sql_query(f"SELECT users.username FROM users WHERE users.id='{userId}';", conn)['username'].iloc[0])  
    totalEngagementOfUsers['username'] = influencer                      
    print(totalEngagementOfUsers.reset_index().drop('index',axis=1))
except Exception as e:
    print(f"An unexpected error occurred: {e}")  

conn.close()
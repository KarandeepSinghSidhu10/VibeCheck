import pandas as pd
from collections import Counter
import emoji

# --- 1. BASIC STATISTICS ---
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    return num_messages, len(words)

# --- 2. BUSIEST USERS ---
def most_busy_users(df):
    df = df[df['user'] != 'group_notification']
    x = df['user'].value_counts().head()
    new_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    new_df.columns = ['name', 'percent']
    return x, new_df

# --- 3. TIMELINE ---
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    timeline = df.groupby(['year', 'month']).count()['message'].reset_index()
    
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
        
    timeline['time'] = time
    return timeline

# --- 4. EMOJI ANALYSIS ---
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([match['emoji'] for match in emoji.emoji_list(message)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    
    if not emoji_df.empty:
        emoji_df.columns = ['emoji', 'count']
        
    return emoji_df

def user_emoji_leaderboard(df):
    df = df[df['user'] != 'group_notification']
    
    users = []
    emoji_counts = []

    unique_users = df['user'].unique()

    for user in unique_users:
        user_df = df[df['user'] == user]
        count = 0
        for message in user_df['message']:
            count += len(emoji.emoji_list(message))
        
        users.append(user)
        emoji_counts.append(count)

    leaderboard = pd.DataFrame({'User': users, 'Emojis Sent': emoji_counts})
    leaderboard = leaderboard.sort_values(by='Emojis Sent', ascending=False).reset_index(drop=True)
    
    return leaderboard.head(10)

# --- 5. ACTIVITY HEATMAP  ---
def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Create pivot table
    user_heatmap = df.pivot_table(index='day_name', columns='hour', values='message', aggfunc='count').fillna(0)
    
    # Force all 24 hours (0-23) to exist, even if empty
    all_hours = range(24)
    user_heatmap = user_heatmap.reindex(columns=all_hours, fill_value=0)
    
    #  Sort days correctly (Monday -> Sunday)
    # Otherwise they might appear alphabetically (Friday first)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    user_heatmap = user_heatmap.reindex(index=days_order, fill_value=0)
    
    return user_heatmap

# --- 6. DAILY TIMELINE ---
def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Group by exact date (Year-Month-Day)
    daily_timeline = df.groupby('message_date').count()['message'].reset_index()
    return daily_timeline

# --- 7. MOST BUSY DAY  ---
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()
# --- 8. MOST BUSY MONTH  ---
def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()
import re
import pandas as pd

def preprocess(data):
    # List of all common WhatsApp date patterns
    patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm]\s-\s',  # 12hr
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',              # 24hr
        r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s?[APap]?[Mm]?\]\s', # iOS Brackets
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s?[APap]?[Mm]?\s'      # iOS No Brackets
    ]

    selected_pattern = None
    for p in patterns:
        if len(re.findall(p, data)) > 0:
            selected_pattern = p
            break
            
    if not selected_pattern:
        return pd.DataFrame(columns=['user', 'message', 'year', 'month', 'day', 'hour', 'minute'])

    messages = re.split(selected_pattern, data)[1:]
    dates = re.findall(selected_pattern, data)
    
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Clean dates
    df['message_date'] = df['message_date'].str.replace('[', '').str.replace(']', '').str.replace(' - ', '').str.strip()
    df['message_date'] = pd.to_datetime(df['message_date'], dayfirst=True, errors='coerce')

    users = []
    msgs = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  
            users.append(entry[1])
            msgs.append(entry[2])
        else:
            users.append('group_notification')
            msgs.append(entry[0])

    df['user'] = users
    df['message'] = msgs
    df.drop(columns=['user_message'], inplace=True)
    
    df['year'] = df['message_date'].dt.year
    df['month'] = df['message_date'].dt.month_name()
    df['day'] = df['message_date'].dt.day
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute
    df['day_name'] = df['message_date'].dt.day_name()

    return df
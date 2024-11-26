import re
import pandas as pd


def preprocess(data):
    # Update the pattern to match both 12-hour and 24-hour time formats
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM|am|pm|-)\s-\s|\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Remove any trailing ' - ' from the date strings
    dates = [date.strip(' -') for date in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date type
    def parse_date(date_str):
        for fmt in ('%d/%m/%Y, %I:%M %p', '%d/%m/%Y, %H:%M'):
            try:
                return pd.to_datetime(date_str, format=fmt)
            except ValueError:
                pass
        raise ValueError(f"no valid date format found for {date_str}")

    df['date'] = df['message_date'].apply(parse_date)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message', 'message_date'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
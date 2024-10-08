import requests
import sqlite3
import time
from datetime import datetime
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
API_KEY = '812bb6e9e3673035e486c96700d41b36'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
INTERVAL = 300  # 5 minutes in seconds
DB_FILE = 'weather_data.db'
ALERT_TEMP_THRESHOLD = 35  # Example threshold for temperature
ALERT_CONSECUTIVE_COUNT = 2  # Number of consecutive breaches to trigger an alert

# Email configuration
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USER = 'your_email@example.com'
SMTP_PASSWORD = 'your_password'
ALERT_EMAIL = 'alert_recipient@example.com'

def fetch_weather_data(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {city}: {response.status_code}")
        return None

def save_to_db(city, data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            city TEXT,
            dt INTEGER,
            temp REAL,
            feels_like REAL,
            weather TEXT
        )
    ''')
    
    # Insert data
    cursor.execute('''
        INSERT INTO weather (city, dt, temp, feels_like, weather)
        VALUES (?, ?, ?, ?, ?)
    ''', (city, data['dt'], data['main']['temp'], data['main']['feels_like'], data['weather'][0]['main']))
    
    conn.commit()
    conn.close()

def compute_daily_summary():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT city, date(dt, 'unixepoch') as date, 
               AVG(temp) as avg_temp, 
               MAX(temp) as max_temp, 
               MIN(temp) as min_temp, 
               weather 
        FROM weather
        GROUP BY city, date
    ''')
    
    summaries = cursor.fetchall()
    conn.close()
    
    # Process and print summaries
    for summary in summaries:
        print(f"City: {summary[0]}, Date: {summary[1]}, Avg Temp: {summary[2]}, Max Temp: {summary[3]}, Min Temp: {summary[4]}, Dominant Weather: {summary[5]}")

def check_alerts():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT city, temp 
        FROM weather 
        WHERE temp > ?
        AND dt > strftime('%s', 'now', '-10 minutes')
    ''', (ALERT_TEMP_THRESHOLD,))
    
    alerts = cursor.fetchall()
    conn.close()

    # Track consecutive breaches for alerting
    breaches = {city: 0 for city in CITIES}
    for city, temp in alerts:
        breaches[city] += 1
        if breaches[city] >= ALERT_CONSECUTIVE_COUNT:
            send_email_alert(city, temp)
            breaches[city] = 0  # Reset after sending alert

def send_email_alert(city, temp):
    subject = f"Temperature Alert for {city}"
    body = f"The temperature in {city} has exceeded the threshold with a current temperature of {temp}°C."
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = ALERT_EMAIL
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Alert email sent for {city}!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def visualize_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT city, date(dt, 'unixepoch') as date, AVG(temp) as avg_temp
        FROM weather
        GROUP BY city, date
    ''')
    
    data = cursor.fetchall()
    conn.close()
    
    # Organize data by city
    city_data = {}
    for row in data:
        city, date, avg_temp = row
        if city not in city_data:
            city_data[city] = ([], [])
        city_data[city][0].append(date)
        city_data[city][1].append(avg_temp)
    
    # Plot for each city
    for city, (dates, avg_temps) in city_data.items():
        plt.figure(figsize=(10, 5))
        plt.plot(dates, avg_temps, marker='o')
        plt.title(f'Average Daily Temperature for {city}')
        plt.xlabel('Date')
        plt.ylabel('Average Temperature (°C)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{city}_temperature_plot.png')
        plt.close()

def main():
    while True:
        for city in CITIES:
            data = fetch_weather_data(city)
            if data:
                save_to_db(city, data)
                
        compute_daily_summary()
        check_alerts()
        visualize_data()
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

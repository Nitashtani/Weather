# Weather Monitoring System

A real-time weather monitoring system that tracks weather conditions, performs daily rollups, triggers alerts, and generates visualizations using data from the OpenWeatherMap API.

## Features

- **Real-time Data Retrieval**: Fetches weather data for multiple cities from the OpenWeatherMap API.
- **Daily Weather Summaries**: Computes and stores daily summaries, including average, maximum, and minimum temperatures, and dominant weather conditions.
- **Alerting System**: Sends alerts via email if temperature thresholds are breached for consecutive updates.
- **Visualizations**: Generates and saves plots of average daily temperatures for each city.

## Getting Started

### Prerequisites

- **Docker**: Required for containerizing and running the application.
- **A valid OpenWeatherMap API Key**: [Sign up here](https://openweathermap.org/api) to get your API key.
- **Email Server Configuration**: An SMTP server is needed for sending alert emails.

### Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your_username/weather-monitoring-system.git
   cd weather-monitoring-system



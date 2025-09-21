# Flight Delay Predictor

A modern Flask web application that predicts flight delays for Chicago O'Hare Airport arrivals based on historical airline and airport data.

## Features

- 🛬 **Real-time Flight Selection**: Choose from a comprehensive list of incoming flights
- 📊 **Delay Prediction**: Get detailed risk assessment with probability percentages
- 📈 **Interactive Charts**: Visualize delay statistics by airline and origin airport
- 🎨 **Modern UI**: Beautiful, responsive design with Bootstrap 5
- 📱 **Mobile Friendly**: Optimized for all device sizes

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
flight-delay-predictor/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── style.css         # Custom CSS styles
    └── script.js         # JavaScript functionality
```

## How It Works

### Delay Prediction Algorithm
The application uses a weighted combination of two factors:
- **Airline Factor (40% weight)**: Historical delay probability for each airline
- **Origin Factor (60% weight)**: Historical delay probability for each origin airport

### Risk Categories
- 🟢 **Low Risk (≤30%)**: Minimal delay probability
- 🟡 **Medium Risk (31-50%)**: Moderate delay probability  
- 🔴 **High Risk (>50%)**: High delay probability

### Data Sources
- Flight data includes real airline codes and airport information
- Delay probabilities are based on historical performance data
- Covers major airlines and airports serving Chicago O'Hare

## API Endpoints

- `GET /` - Main application page
- `GET /api/flights` - Get list of all available flights
- `GET /api/predict/<flight_id>` - Get delay prediction for specific flight
- `GET /api/charts/airline` - Get airline delay statistics chart
- `GET /api/charts/origin` - Get origin airport delay statistics chart
- `GET /api/charts/combined` - Get overall delay risk distribution chart

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Charts**: Matplotlib (converted to base64 images)
- **Data Processing**: Pandas, NumPy
- **Icons**: Font Awesome 6

## Customization

### Adding New Airlines
Edit the `airline_delay_prob` dictionary in `app.py`:
```python
airline_delay_prob = {
    'New Airline': 45,  # Add your airline here
    # ... existing airlines
}
```

### Adding New Airports
Edit the `origin_delay_prob` dictionary in `app.py`:
```python
origin_delay_prob = {
    'New Airport': 35,  # Add your airport here
    # ... existing airports
}
```

### Modifying Risk Thresholds
Update the risk calculation logic in the `predict_flight_delay()` function:
```python
if combined_prob <= 30:      # Low risk threshold
    risk = "LOW RISK"
elif combined_prob <= 50:    # Medium risk threshold
    risk = "MEDIUM RISK"
else:
    risk = "HIGH RISK"
```

## Development

### Running in Debug Mode
```bash
export FLASK_ENV=development
python app.py
```

### Adding New Features
1. Add new routes in `app.py`
2. Update the HTML template in `templates/index.html`
3. Add JavaScript functionality in `static/script.js`
4. Style new elements in `static/style.css`

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

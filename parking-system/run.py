"""
Entry point for the Smart Parking Slot System.

Run with:   python run.py
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # host="0.0.0.0" so you can also open the app from your phone on the same Wi-Fi.
    app.run(host="0.0.0.0", port=5000, debug=True)
import os
from app import create_app, AppMode

# Create the Flask app in the desired mode (default is debug mode)
app = create_app(mode=AppMode.DEBUG)

if __name__ == "__main__":
    # Run the app on the desired port (default is 8123)
    app.run(host="0.0.0.0", port=os.getenv("PORT", default=8123), threaded=True)

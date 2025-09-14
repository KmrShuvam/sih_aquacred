"""
Local development shim for the Flask application.
For Vercel deployment, the entry point is api/index.py
"""
from api.index import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
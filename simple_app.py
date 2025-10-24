#!/usr/bin/env python3
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Quip Uploader - Test</title></head>
    <body>
        <h1>🚀 Quip Document Uploader</h1>
        <p>✅ Flask is working!</p>
        <p>🔗 <a href="/login">Go to Login</a></p>
    </body>
    </html>
    '''

@app.route('/login')
def login():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Login</title></head>
    <body>
        <h1>🔐 Login</h1>
        <p>Test login page working!</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Starting simple test server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

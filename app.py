from flask import Flask, request, render_template, redirect
import hashlib
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        # Generate a hash of the URL
        hash_object = hashlib.sha256(url.encode())
        hex_dig = hash_object.hexdigest()
        # Check if the hash already exists in the database
        conn = sqlite3.connect('urls.db')
        c = conn.cursor()
        c.execute('SELECT short_url FROM urls WHERE hash = ?', (hex_dig,))
        result = c.fetchone()
        if result is not None:
            # If the hash already exists, generate a new hash
            # until a unique one is found
            while result is not None:
                hash_object = hashlib.sha256((url + str(result[0])).encode())
                hex_dig = hash_object.hexdigest()
                c.execute('SELECT short_url FROM urls WHERE hash = ?', (hex_dig,))
                result = c.fetchone()
        # Truncate the hash to create a shortened URL
        short_url = "https://البحرين.١١-فريق/" + hex_dig[:8]
        # Save the URL mapping to the database
        c.execute('INSERT INTO urls (original_url, short_url, hash) VALUES (?, ?, ?)', (url, short_url, hex_dig))
        conn.commit()
        conn.close()
        # Render the shortened URL page
        return render_template('shortened.html', short_url=short_url)
    else:
        return render_template('home.html')

@app.route('/<short_url>')
def redirect_to_original(short_url):
    # Look up the original URL in the database
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
    result = c.fetchone()
    conn.close()
    if result is not None:
        # Redirect the user to the original URL
        return redirect(result[0])
    else:
        # Show an error message if the URL was not found
        return 'URL not found'

if __name__ == '__main__':
    # Create the URL mapping database if it doesn't exist
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS urls (original_url TEXT, short_url TEXT, hash TEXT)')
    conn.close()
    # Start the Flask application
    app.run(debug=True)
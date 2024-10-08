import os
from flask import Flask, request, jsonify
import instaloader
from flask_cors import CORS 
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Instaloader
loader = instaloader.Instaloader()

# Retrieve credentials from environment variables
USERNAME = os.getenv('INSTALOADER_USERNAME')
PASSWORD = os.getenv('INSTALOADER_PASSWORD')

if not USERNAME or not PASSWORD:
    logger.error("Instagram credentials are not set in environment variables.")
    raise ValueError("Instagram credentials are not set in environment variables.")

# Log in to Instagram
try:
    loader.login(USERNAME, PASSWORD)
    logger.info("Logged in to Instagram successfully.")
except instaloader.exceptions.BadCredentialsException:
    logger.error("Invalid credentials, please check your username and password.")
    raise
except instaloader.exceptions.TwoFactorAuthRequiredException:
    logger.error("Two-factor authentication is enabled on this account. Please handle 2FA.")
    raise
except instaloader.exceptions.ConnectionException as ce:
    logger.error(f"Connection error during login: {str(ce)}")
    raise
except Exception as e:
    logger.error(f"An error occurred during login: {str(e)}")
    raise

@app.route('/profile', methods=['GET'])
def get_profile():
    username = request.args.get('username')  # Get username from query parameters

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    try:
        # Load the profile
        profile = instaloader.Profile.from_username(loader.context, username)

        # Prepare the profile data
        profile_data = {
            'username': profile.username,
            'full_name': profile.full_name,
            'bio': profile.biography,
            'followers': profile.followers,
            'following': profile.followees,
            'posts': profile.mediacount,
        }

        return jsonify(profile_data), 200

    except instaloader.exceptions.ProfileNotExistsException:
        return jsonify({'error': 'Profile not found'}), 404

    except instaloader.exceptions.ConnectionException as ce:
        # Handle connection issues
        return jsonify({'error': 'Connection error. Please try again later.'}), 503

    except instaloader.exceptions.BadCredentialsException:
        return jsonify({'error': 'Invalid Instagram credentials.'}), 401

    except instaloader.exceptions.TwoFactorAuthRequiredException:
        return jsonify({'error': 'Two-factor authentication is required.'}), 401

    except Exception as e:
        # Log the exception details for debugging
        app.logger.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

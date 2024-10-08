from flask import Flask, request, jsonify
import instaloader
from flask_cors import CORS 

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Initialize Instaloader
loader = instaloader.Instaloader()

# Login credentials (replace with your credentials)
USERNAME = 'scr.ipptify'  # Replace with your Instagram username
PASSWORD = 'mino05varsh06'    # Replace with your Instagram password

# Log in to Instagram
try:
    loader.login(USERNAME, PASSWORD)  # Log in with the provided credentials
except instaloader.exceptions.BadCredentialsException:
    print("Invalid credentials, please check your username and password.")
except Exception as e:
    print(f"An error occurred during login: {str(e)}")

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
            'fullname': profile.full_name,
            'bio': profile.biography,
            'followers': profile.followers,
            'following': profile.followees,
            'posts': profile.mediacount,
        }

        return jsonify(profile_data), 200

    except instaloader.exceptions.ProfileNotExistsException:
        return jsonify({'error': 'Profile not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '_main_':
    app.run(debug=True, port=5000)
# DiscordSnowballFightBot

Have snowball fights with your discord friends ^w^

## Setup

This project requires a Google Firebase.

Create a .env file and place your Discord token in it like so:

```
DISCORD_TOKEN=your_discord_token
```

Then download your Firebase certificate and update `snowball.py` to point to that file:

```python
# line 13
cred_obj = firebase_admin.credentials.Certificate('your_certificate_file_here.json')
```

Also update the Firebase url in `snowball.py` to point to your Firebase

```python
# line 14
self.default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': 'https://your-firebase-url.firebaseio.com/'
})
```

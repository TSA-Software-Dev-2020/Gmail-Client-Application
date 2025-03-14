import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True


SEND_FILE_MAX_AGE_DEFAULT = 0


# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = str(os.urandom(24))

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')

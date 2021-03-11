from application import create_app
import logging
import os

# Default config_file is dev
app = create_app()

if __name__ == '__main__':
    # Default port set to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# hello
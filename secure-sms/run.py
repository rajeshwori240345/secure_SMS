"""Application entrypoint for the Secure SMS Flask project.

This file simply creates the Flask application by calling
``create_app`` from the ``app`` package and runs it when executed
directly.  Keeping the entrypoint minimal makes it easy to import
the app in tests while allowing the built-in Flask development
server to be used when run from the command line.
"""

from app import create_app


# Create the Flask application instance.  This is imported in test
# modules (see tests/test_health.py) to obtain a test client.
app = create_app()


if __name__ == "__main__":
    # Run the development server if this script is executed directly.  The
    # debug flag enables live reload and better error messages during
    # development.  In production you would run via a WSGI server.
    app.run(debug=True)
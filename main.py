from app import create_app
import os

if __name__ == '__main__':
    app = create_app()

    # Development server run keren
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
    print("🚀 Flask application running on http://localhost:5000")
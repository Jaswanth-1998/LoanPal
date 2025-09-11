from app import app
import routes  # noqa: F401
import os

if __name__ == "__main__":
    # Ensure upload directory exists
    upload_dir = os.path.join(app.root_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    app.run(host="0.0.0.0", port=5000, debug=True)
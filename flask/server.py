from waitress import serve
import app
if __name__ == '__main__':
    serve(app.app, host='0.0.0.0', port=8080)

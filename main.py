from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/<int:vid>')
def serve_view(vid):
    return 'Hello viewer id '+str(vid)

if __name__=='__main__':
    app.run('0.0.0.0','5000')

from flask import Flask, render_template
app = Flask(__name__, static_folder='static', template_folder='./')


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')

if __name__ == '__main__':

  app.run(host='192.168.1.216', port=20595, debug=True)
 
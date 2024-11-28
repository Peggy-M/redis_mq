
from flask import Flask

from com.cgnpc.service.function import training_fun

app = Flask(__name__)

@app.route('/trainingModel', methods=['POST'])
def training_model(filePath=None):
    training_fun(filePath)


if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')

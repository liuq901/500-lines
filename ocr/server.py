import http.server
import json

import numpy as np

from ocr import OCRNeuralNetwork

HOST_NAME = 'localhost'
PORT_NUMBER = 8000
HIDDEN_NODE_COUNT = 25

data_matrix = np.loadtxt(open('data.csv', 'rb'), delimiter=',')
data_labels = np.loadtxt(open('dataLabels.csv', 'rb'))

data_matrix = data_matrix.tolist()
data_labels = data_labels.tolist()

assert len(data_matrix) == len(data_labels) == 5000

nn = OCRNeuralNetwork(HIDDEN_NODE_COUNT, data_matrix, data_labels, list(range(5000)))

class JSONHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        response_code = 200
        response = '*'
        var_len = int(self.headers.get('Content-Length'))
        content = self.rfile.read(var_len)
        payload = json.loads(content)

        if payload.get('train'):
            nn.train(payload['trainArray'])
            nn.save()
        elif payload.get('predict'):
            try:
                response = {'type': 'test', 'result': nn.predict(str(payload['image']))}
            except:
                response_code = 500
        else:
            response_code = 400

        self.send_response(response_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        if response:
            self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), JSONHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    else:
        print('Unexpected server exception occurred.')
    finally:
        httpd.server_close()

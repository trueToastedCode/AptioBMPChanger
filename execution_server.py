from flask import Flask, request, Response
import subprocess

HOST = '0.0.0.0'
PORT = '8080'

def execute_command(command: str):
    try:
        subprocess.check_call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute():
    r = execute_command(str(request.data)[2:-1])
    return Response(status=200 if r else 500)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)

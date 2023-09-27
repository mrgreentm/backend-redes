import psutil
import GPUtil
from flask import Flask, Response, json
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Função para obter o uso de CPU, GPU e RAM em tempo real
def get_usage_data():
    while True:
        # Obtém o uso de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Obtém o uso de GPU
        try:
            gpu = GPUtil.getGPUs()[0]
            gpu_percent = gpu.load * 100
        except Exception as e:
            gpu_percent = 0
        
        # Obtém o uso de RAM
        ram = psutil.virtual_memory()
        ram_percent = ram.percent

        event_data = {
            'cpu': cpu_percent,
            'gpu': gpu_percent,
            'memory': ram_percent
        }

        event_json = json.dumps(event_data)

        yield f"data: {event_json}\n\n"

# Rota para o streaming de dados de uso de CPU, GPU e RAM
@app.route('/usage-data')
def usage_data():
    return Response(get_usage_data(), content_type='text/event-stream')


if __name__ == '__main__':
    # Executar o aplicativo Flask
    app.run(host='127.0.0.1', port=5000, threaded=True)
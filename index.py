import psutil
import GPUtil
import socket
import threading
from flask import Flask, Response

app = Flask(__name__)

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

        yield f"data: {cpu_percent},{gpu_percent},{ram_percent}\n\n"

# Rota para o streaming de dados de uso de CPU, GPU e RAM
@app.route('/usage-data')
def usage_data():
    return Response(get_usage_data(), content_type='text/event-stream')

# Rota inicial para exibir a página HTML com os gráficos de barras
@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Monitor de Uso de CPU, GPU e RAM</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
    </head>
    <body>
        <h1>Uso de CPU, GPU e RAM em Tempo Real (Gráficos de Barras)</h1>
        <div style="width: 50%">
            <canvas id="cpu-gpu-ram-chart"></canvas>
        </div>
        <script>
            const ctx = document.getElementById('cpu-gpu-ram-chart').getContext('2d');

            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['CPU', 'GPU', 'RAM'],
                    datasets: [{
                        label: 'Uso (%)',
                        backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'],
                        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
                        borderWidth: 1,
                        data: [0, 0, 0],
                    }],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                        },
                    },
                },
            });

            const eventSource = new EventSource('/usage-data');
            eventSource.onmessage = function(event) {
                const [cpu, gpu, ram] = event.data.split(',');
                chart.data.datasets[0].data = [cpu, gpu, ram];
                chart.update();
            };
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # Executar o aplicativo Flask
    app.run(host=socket.gethostname(), port=5000, threaded=True)

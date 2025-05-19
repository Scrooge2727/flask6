import matplotlib.pyplot as plt
import requests

# Получаем метрики с /metrics
response = requests.get("http://localhost:8000/metrics")
data = response.text

# Парсим метрики (упрощённо)
request_counts = []
for line in data.split("\n"):
    if "http_requests_total" in line and "GET" in line:
        count = float(line.split()[-1])
        request_counts.append(count)

# Рисуем график
plt.plot(request_counts, label="HTTP Requests")
plt.title("API Request Traffic")
plt.xlabel("Time (requests)")
plt.ylabel("Count")
plt.legend()
plt.show()
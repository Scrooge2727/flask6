import connexion
from swagger_server import encoder
from swagger_server.sqldate import db  # Импортируем объект базы данных
from prometheus_client import Counter, Summary, Gauge, Histogram, generate_latest
from swagger_server.logger import logger
from swagger_server.tracer import configure_tracing  # Импортируем функцию из tracer.py
from flask import Response
import time
import random


# ===== Создаём метрики =====

# 1. Основные метрики запросов
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
)

REQUEST_TIME = Summary(
    'http_request_duration_seconds',
    'Request processing time',
    ['method', 'endpoint'],
)

# 2. Метрики для бизнес-логики (пример для API заметок)
NEW_CREATED = Counter(
    'notes_created_total',
    'Total notes created',
    ['method', 'endpoint'],
)

NEW_DELETED = Counter(
    'notes_deleted_total',
    'Total notes deleted',
)

# 3. Системные метрики
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Process memory usage',
)

CPU_LOAD = Gauge(
    'cpu_load_percent',
    'Simulated CPU load',
)

# 4. Гистограмма для анализа распределения
RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'Response size distribution',
    buckets=[100, 500, 1000, 5000, 10000],
)


def track_metrics(response):
    """Логируем метрики после каждого запроса."""
    if hasattr(connexion.request, 'url_rule'):
        endpoint = connexion.request.url_rule.rule
        method = connexion.request.method
        status = response.status_code

        # Замер времени и размера ответа
        duration = time.time() - connexion.request.start_time
        REQUEST_TIME.labels(method, endpoint).observe(duration)
        REQUEST_COUNT.labels(method, endpoint, str(status)).inc()

        if endpoint == '/api/new' and method == 'POST':
            NEW_CREATED.labels(method, endpoint).inc()
        elif endpoint == '/api/new/{new_entity_id}' and method == 'DELETE':
            NEW_DELETED.inc()

        # Логируем размер ответа (примерно)
        if response.is_json:
            RESPONSE_SIZE.observe(len(response.get_data()))

    return response


def update_system_metrics():
    """Обновляем системные метрики (пример)."""
    MEMORY_USAGE.set(random.randint(100, 500))  # Имитация использования памяти
    CPU_LOAD.set(random.uniform(0.1, 5.0))  # Имитация нагрузки CPU


def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder

    # Middleware для метрик
    app.app.before_request(lambda: setattr(connexion.request, 'start_time', time.time()))
    app.app.after_request(track_metrics)

    # Инициализация API из swagger.yaml
    app.add_api('swagger.yaml', arguments={'title': 'database API'}, pythonic_params=True)

    # Конфигурация SQLAlchemy для SQLite
    app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app.app)

    # Создаём таблицы, если их нет
    with app.app.app_context():
        db.create_all()

    # Эндпоинт для метрик
    @app.app.route('/metrics')
    def metrics():
        update_system_metrics()  # Обновляем системные метрики перед отдачей
        return Response(generate_latest(), mimetype='text/plain')

    logger.info("Сервер запущен")

    # Настройка трассировки с использованием функции из tracer.py
    configure_tracing(app)
    app.run(port=5000)


if __name__ == '__main__':
    main()

import requests
import logging
from config.settings import API_URL
from datetime import datetime, timedelta, timezone

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_weekly_uptime_percent(uptime_seconds: float, last_check_timestamp: int) -> float:
    """
    Рассчитывает недельный аптайм в процентах на основе переданного значения uptime
    и количества секунд, прошедших с последнего четверга 00:00 UTC на момент последней проверки.

    Args:
        uptime_seconds (float): Аптайм сервера в секундах.
        last_check_timestamp (int): Метка времени последней проверки в миллисекундах (Unix-время).

    Returns:
        float: Недельный аптайм в процентах.
    """
    last_check_datetime = datetime.fromtimestamp(last_check_timestamp / 1000, tz=timezone.utc)
    days_since_thursday = (last_check_datetime.weekday() + 3) % 7
    last_thursday = last_check_datetime - timedelta(
        days=days_since_thursday,
        hours=last_check_datetime.hour,
        minutes=last_check_datetime.minute,
        seconds=last_check_datetime.second,
        microseconds=last_check_datetime.microsecond,
    )
    total_seconds_since_thursday = (last_check_datetime - last_thursday).total_seconds()
    uptime_percent = (uptime_seconds / total_seconds_since_thursday) * 100 if total_seconds_since_thursday > 0 else 0
    return min(uptime_percent, 100)


async def parse_node(ip: str) -> dict | None:
    """
    Получает данные ноды по IP-адресу из API, рассчитывает аптайм и возвращает сводную информацию.

    Args:
        ip (str): IP-адрес ноды.

    Returns:
        dict | None: Словарь с информацией о ноде или None, если данные не были получены.
    """
    url = f"{API_URL}{ip}"
    try:
        response = requests.get(url, timeout=10)  # Устанавливаем тайм-аут
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к API для IP {ip}: {e}")
        return None

    data = response.json()

    all_nums = data["pagination"]["totalItems"]
    eligible_nodes = data["totalEligibleNodes"]
    percent_eligible = (eligible_nodes / all_nums) * 100

    total_uptime_percent = 0
    nodes_with_90_percent_uptime = 0

    for node in data['nodes']:
        uptime_seconds = node['_source'].get('uptime', 0)
        last_check = node['_source'].get('lastCheck', 0)
        weekly_uptime_percent = calculate_weekly_uptime_percent(uptime_seconds, last_check)
        total_uptime_percent += weekly_uptime_percent
        logger.debug(f"Нода {node['_source'].get('id')} имеет аптайм {weekly_uptime_percent:.2f}% за последнюю неделю")

        if weekly_uptime_percent >= 90:
            nodes_with_90_percent_uptime += 1

    average_uptime = total_uptime_percent / all_nums if all_nums > 0 else 0

    info = {
        "ip_server": ip,
        "all_nums": all_nums,
        "eligible_nodes": eligible_nodes,
        "percent_eligible": percent_eligible,
        "nodes_with_90_percent_uptime": nodes_with_90_percent_uptime,
        "average_uptime": average_uptime,
    }
    return info

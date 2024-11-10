import aiosqlite
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def init_db() -> None:
    """
    Инициализирует базу данных, создавая таблицу `users`, если она не существует.

    Таблица `users` содержит два поля:
        - `user_id` (INTEGER PRIMARY KEY): уникальный идентификатор пользователя.
        - `ip_addresses` (TEXT): строка с IP-адресами, разделенными запятыми.
    """
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                ip_addresses TEXT
            )
        """)
        await db.commit()
    logger.info("База данных инициализирована и таблица `users` проверена/создана.")

async def get_user_ips(user_id: int) -> str | None:
    """
    Возвращает строку IP-адресов для пользователя с указанным `user_id`.

    Args:
        user_id (int): уникальный идентификатор пользователя Telegram.

    Returns:
        str | None: строка с IP-адресами, разделенными запятыми, или `None`, если пользователь не найден.
    """
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT ip_addresses FROM users WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                logger.info(f"Получены IP-адреса для пользователя {user_id}: {result[0]}")
                return result[0]
            else:
                logger.warning(f"IP-адреса для пользователя {user_id} не найдены.")
                return None

async def update_user_ips(user_id: int, ip_addresses: str) -> None:
    """
    Обновляет IP-адреса пользователя с указанным `user_id`, очищая пробелы вокруг IP.
    Если запись для пользователя существует, она обновляется; иначе создается новая.

    Args:
        user_id (int): уникальный идентификатор пользователя Telegram.
        ip_addresses (str): строка с IP-адресами, разделенными запятыми.

    Очистка данных:
        - Удаляет лишние пробелы вокруг каждого IP-адреса.
        - Пропускает пустые элементы в случае лишних запятых.
    """
    # Очистка пробелов вокруг IP-адресов
    cleaned_ips = ",".join(ip.strip() for ip in ip_addresses.split(",") if ip.strip())
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            INSERT INTO users (user_id, ip_addresses)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET ip_addresses=excluded.ip_addresses
        """, (user_id, cleaned_ips))
        await db.commit()
    logger.info(f"IP-адреса пользователя {user_id} обновлены: {cleaned_ips}")

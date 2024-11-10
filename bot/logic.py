import logging
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from bot.db import get_user_ips, update_user_ips
from parser.logic import parse_node

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
logger = logging.getLogger(__name__)

standard_handler_router = Router()

# Обработчик команды /start
@standard_handler_router.message(CommandStart())
async def start_command(message: types.Message):
    """
    Обработчик команды /start.

    Если у пользователя уже есть сохраненные IP-адреса, они будут показаны.
    Если данных нет, запрашивает у пользователя ввод IP-адресов серверов для отслеживания.

    Args:
        message (types.Message): Сообщение, вызвавшее команду.
    """
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вызвал команду /start")

    current_ips = await get_user_ips(user_id)
    if current_ips:
        formatted_ips = "\n".join(current_ips.split(","))
        logger.info(f"Пользователь {user_id} уже имеет сохраненные IP-адреса: {current_ips}")
        await message.reply(f"Ваши текущие IP-адреса для отслеживания:\n{formatted_ips}\n\n"
                            "Если хотите изменить список, введите команду /ip.")
    else:
        logger.info(f"У пользователя {user_id} нет сохраненных IP-адресов")
        await message.reply("Привет! Введите IP-адреса серверов, которые хотите отслеживать, через запятую:")
# Обработчик ввода IP-адресов
@standard_handler_router.message(lambda message: message.text and "," in message.text)
async def handle_ip_input(message: types.Message):
    """
    Обрабатывает ввод IP-адресов пользователем, разделенных запятыми.

    Сохраняет IP-адреса в базе данных и подтверждает сохранение.

    Args:
        message (types.Message): Сообщение с введенными IP-адресами.
    """
    user_id = message.from_user.id
    ip_addresses = message.text
    await update_user_ips(user_id, ip_addresses)
    logger.info(f"IP-адреса {ip_addresses} сохранены для пользователя {user_id}")
    await message.reply("IP-адреса успешно сохранены! Используйте /check для проверки или /ip для изменения адресов.")

# Обработчик команды /ip для изменения IP-адресов
@standard_handler_router.message(Command("ip"))
async def ip_command(message: types.Message):
    """
    Обработчик команды /ip для отображения текущих IP-адресов и их изменения.

    Если у пользователя уже есть сохраненные IP-адреса, они будут показаны,
    и предложено ввести новые для замены. Если данных нет, предлагает ввести новые IP-адреса.

    Args:
        message (types.Message): Сообщение, вызвавшее команду.
    """
    user_id = message.from_user.id
    current_ips = await get_user_ips(user_id)
    if current_ips:
        await message.reply(f"Ваши текущие IP-адреса: {current_ips}\nВведите новые IP-адреса для замены:")
        logger.info(f"Пользователь {user_id} запросил текущие IP-адреса: {current_ips}")
    else:
        await message.reply("У вас еще не сохранены IP-адреса. Введите IP-адреса для отслеживания:")
        logger.warning(f"У пользователя {user_id} нет сохраненных IP-адресов")

# Обработчик команды /check для проверки серверов
@standard_handler_router.message(Command("check"))
async def check_command(message: types.Message):
    """
    Обработчик команды /check для проверки состояния серверов.

    Получает сохраненные IP-адреса пользователя, вызывает `parse_node` для каждого адреса,
    собирает данные и отображает информацию о серверах, включая общее количество нод,
    eligible-нод, их процент, количество нод с аптаймом 90%+ и средний аптайм.

    Args:
        message (types.Message): Сообщение, вызвавшее команду.
    """
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /check")
    user_id = message.from_user.id
    ip_addresses = await get_user_ips(user_id)
    if not ip_addresses:
        await message.reply("У вас еще не сохранены IP-адреса. Введите IP-адреса для отслеживания через /ip.")
        logger.warning(f"Пользователь {user_id} попытался выполнить /check без сохраненных IP-адресов")
        return

    ips = ip_addresses.split(",")
    total_nodes = 0
    total_eligible = 0
    total_nodes_with_90_uptime = 0
    total_average_uptime = 0
    results = []

    for ip in ips:
        info = await parse_node(ip.strip())
        if info:
            results.append(
                f"Сервер {info['ip_server']}:\n"
                f"  Всего нод: {info['all_nums']}\n"
                f"  Eligible: {info['eligible_nodes']}\n"
                f"  Процент Eligible: {info['percent_eligible']:.2f}%\n"
                f"  Нод с 90%+ аптаймом: {info['nodes_with_90_percent_uptime']}\n"
                f"  Средний аптайм: {info['average_uptime']:.2f}%"
                f"\n"
            )
            logger.info(f"Проверка сервера {ip}: {info}")
            total_nodes += info["all_nums"]
            total_eligible += info["eligible_nodes"]
            total_nodes_with_90_uptime += info["nodes_with_90_percent_uptime"]
            total_average_uptime += info["average_uptime"] * info["all_nums"]  # для взвешенного среднего
        else:
            results.append(f"Сервер {ip}: не удалось получить данные.")
            logger.warning(f"Не удалось получить данные для сервера {ip}")

    if total_nodes > 0:
        overall_percentage = (total_eligible / total_nodes) * 100
        average_uptime_across_servers = total_average_uptime / total_nodes
        total_nodes_with_90_uptime_percentage = (total_nodes_with_90_uptime / total_nodes) * 100

        results.append(
            f"\nОбщая информация:\n"
            f"  Всего нод: {total_nodes}\n"
            f"  Eligible: {total_eligible}\n"
            f"  Процент Eligible: {overall_percentage:.2f}%\n"
            f"  Нод с 90%+ аптаймом: {total_nodes_with_90_uptime}\n"
            f"  Процент нод с 90%+ аптаймом: {total_nodes_with_90_uptime_percentage:.2f}%\n"
            f"  Средний аптайм по всем нодам: {average_uptime_across_servers:.2f}%"
        )
        logger.info(f"Итоговая статистика для пользователя {user_id}: {results[-1]}")

    await message.reply("\n".join(results))

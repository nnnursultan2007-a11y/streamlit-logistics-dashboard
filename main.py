from functools import reduce

from cities import cities
from warehouses import warehouses
from orders import orders
from vehicles import vehicles


# =========================
# ЛЯМБДА
# =========================

def total_weight(orders):
    weights = map(
        lambda order: order[2],
        orders
    )

    return reduce(
        lambda a, b: a + b,
        weights,
        0
    )


def get_order_ids(orders):
    return tuple(
        map(
            lambda order: order[0],
            orders
        )
    )


# =========================
# ЗАМЫКАНИЯ
# =========================

def by_status(status):
    def check(order):
        return order[3] == status

    return check


def by_weight_range(lo, hi):
    def check(order):
        return lo <= order[2] <= hi

    return check


def by_wh(wh_id):
    def check(order):
        return order[1] == wh_id

    return check


def filter_orders(orders, filter_function):
    return tuple(
        filter(
            filter_function,
            orders
        )
    )


# =========================
# РЕКУРСИЯ №1
# =========================

routes = (
    "Алматы -> Астана",
    "Астана -> Ташкент",
    "Ташкент -> Бишкек",
    "Бишкек -> Душанбе",
    "Душанбе -> Ашхабад",
    "Ашхабад -> Баку",
    "Баку -> Ереван",
    "Ереван -> Тбилиси",
    "Тбилиси -> Минск",
    "Минск -> Москва",
)


def traverse_routes(routes, idx=0):
    if idx >= len(routes):
        return ()

    return (
        routes[idx],
    ) + traverse_routes(routes, idx + 1)


# =========================
# РЕКУРСИЯ №2
# =========================

def build_queue_tree(orders, wh_id):
    if len(orders) == 0:
        return ()

    first_order = orders[0]
    rest_orders = orders[1:]

    if first_order[1] == wh_id:
        return (
            first_order,
        ) + build_queue_tree(rest_orders, wh_id)

    return build_queue_tree(rest_orders, wh_id)


# =========================
# ПОИСК ГОРОДА
# =========================

def get_city_name(city_id):
    for city in cities:
        if city[0] == city_id:
            return city[1]

    return "Не найден"


def get_warehouse_city(warehouse_id):
    for warehouse in warehouses:
        if warehouse[0] == warehouse_id:
            return get_city_name(warehouse[2])

    return "Не найден"


# =========================
# ОСНОВНАЯ ПРОГРАММА
# =========================

if __name__ == "__main__":

    print("======================================")
    print("ЛАБОРАТОРНАЯ РАБОТА №2")
    print("Лямбда и замыкания + рекурсия")
    print("======================================")

    print()
    print("Количество городов:", len(cities))
    print("Количество складов:", len(warehouses))
    print("Количество заказов:", len(orders))
    print("Количество машин:", len(vehicles))

    print()
    print("Общий вес заказов:", total_weight(orders), "кг")

    # Фильтр по статусу
    ready_filter = by_status("ready")
    ready_orders = filter_orders(orders, ready_filter)

    print()
    print("Готовых заказов:", len(ready_orders))

    # Фильтр по весу
    weight_filter = by_weight_range(500, 800)
    weight_orders = filter_orders(orders, weight_filter)

    print("Заказов весом 500-800 кг:", len(weight_orders))

    # Фильтр по складу
    warehouse_filter = by_wh(1)
    warehouse_orders = filter_orders(
        orders,
        warehouse_filter
    )

    print("Заказов на складе №1:", len(warehouse_orders))

    # Город склада
    print(
        "Город склада №1:",
        get_warehouse_city(1)
    )

    # Рекурсивные маршруты
    print()
    print("Маршруты:")

    for route in traverse_routes(routes):
        print("-", route)

    # Рекурсивная очередь
    print()
    print("Заказы склада №2:")

    queue_orders = build_queue_tree(
        orders,
        2
    )

    for order in queue_orders:
        print(
            "ID:", order[0],
            "| Вес:", order[2],
            "| Статус:", order[3]
        )
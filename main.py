from functools import reduce, lru_cache
from itertools import permutations
from time import perf_counter
from typing import Callable, NamedTuple

from containers import Maybe, Just, Nothing, Either, Left, Right
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
# ЛАБОРАТОРНАЯ №3
# ПРОДВИНУТАЯ РЕКУРСИЯ + МЕМОИЗАЦИЯ
# =========================

# Вспомогательные функции Лабы №3
# Нужны для получения данных о заказе и складе.
def get_order(order_id):
    for order in orders:
        if order[0] == order_id:
            return order
    return None


def get_warehouse(warehouse_id, wh_data):
    for wh in wh_data:
        if wh[0] == warehouse_id:
            return wh
    return None


def get_city_id_for_order(order_id, wh_data):
    order = get_order(order_id)
    if order is None:
        return None

    wh = get_warehouse(order[1], wh_data)
    if wh is None:
        return None

    return wh[2]


def route_distance(order_ids, wh_data):
    """Условная дистанция: разница ID городов * 100 км."""
    if len(order_ids) < 2:
        return 0

    distance = 0

    for i in range(len(order_ids) - 1):
        city_a = get_city_id_for_order(order_ids[i], wh_data)
        city_b = get_city_id_for_order(order_ids[i + 1], wh_data)

        if city_a is None or city_b is None:
            return 0

        distance += abs(city_a - city_b) * 100

    return distance


# ЗАДАНИЕ 1А. ПОИСК БЛИЖАЙШЕГО СОСЕДА
def nearest_neighbor_route(order_ids, wh_data):
    """Быстрый приближённый маршрут по принципу ближайшего соседа."""
    if len(order_ids) <= 1:
        return tuple(order_ids)

    remaining = list(order_ids)
    result = [remaining.pop(0)]

    while remaining:
        current_city = get_city_id_for_order(result[-1], wh_data)

        next_order = min(
            remaining,
            key=lambda order_id: abs(
                current_city - get_city_id_for_order(order_id, wh_data)
            )
        )

        result.append(next_order)
        remaining.remove(next_order)

    return tuple(result)


def choose_vehicle(order_ids, vehicle_data):
    """Выбирает доступную машину с достаточной грузоподъёмностью."""
    total = sum(
        get_order(order_id)[2]
        for order_id in order_ids
        if get_order(order_id) is not None
    )

    available = [
        vehicle
        for vehicle in vehicle_data
        if vehicle[3] and vehicle[2] >= total
    ]

    if not available:
        return None

    return min(available, key=lambda vehicle: vehicle[2])


# ЗАДАНИЕ 1Б. ПОЛНЫЙ ПЕРЕБОР
def _compute_route(order_ids, wh_data, vehicle_data):
    """Полный перебор всех вариантов маршрута."""
    if not order_ids:
        return {
            "distance": 0,
            "duration": 0,
            "vehicle_id": None
        }

    vehicle = choose_vehicle(order_ids, vehicle_data)

    if vehicle is None:
        return {
            "distance": 0,
            "duration": 0,
            "vehicle_id": None
        }

    best_distance = None

    for route in permutations(order_ids):
        distance = route_distance(route, wh_data)

        if best_distance is None or distance < best_distance:
            best_distance = distance

    # Для учебной модели считаем среднюю скорость машины 60 км/ч.
    duration = best_distance // 60

    return {
        "distance": best_distance,
        "duration": duration,
        "vehicle_id": vehicle[0]
    }


# ЗАДАНИЕ 1В. МЕМОИЗАЦИЯ / КЭШ
# Повторный вызов с теми же данными берётся из памяти.
@lru_cache(maxsize=None)
def compute_route(order_ids, wh_data, vehicle_data):
    """
    Кэшируемая чистая функция.

    Возвращает:
    {
        "distance": int,
        "duration": int,
        "vehicle_id": int
    }
    """
    return _compute_route(order_ids, wh_data, vehicle_data)


# ЗАДАНИЕ 2. ЗАМЕР ПРОИЗВОДИТЕЛЬНОСТИ
def measure_route_cache(order_ids, wh_data, vehicle_data):
    """Сравнивает время первого вызова и повторного вызова из кэша."""
    compute_route.cache_clear()

    start = perf_counter()
    first_result = compute_route(order_ids, wh_data, vehicle_data)
    first_time = perf_counter() - start

    start = perf_counter()
    second_result = compute_route(order_ids, wh_data, vehicle_data)
    second_time = perf_counter() - start

    return {
        "result": second_result,
        "first_time": first_time,
        "second_time": second_time,
        "speedup": (
            first_time / second_time
            if second_time > 0
            else float("inf")
        ),
        "cache_info": compute_route.cache_info()
    }


# ЗАДАНИЕ 3. UI / REPORTS
def show_best_route_report():
    """Reports → Лучший маршрут (cached)."""
    # 4 заказа дают заметную разницу между полным перебором и кэшем.
    selected_orders = (orders[0], orders[2], orders[7], orders[15])
    order_ids = get_order_ids(selected_orders)

    result = measure_route_cache(
        order_ids,
        warehouses,
        vehicles
    )

    print()
    print("======================================")
    print("REPORTS")
    print("Лучший маршрут (cached)")
    print("======================================")
    print("Заказы:", order_ids)
    print("Расстояние:", result["result"]["distance"], "км")
    print("Время:", result["result"]["duration"], "ч")
    print("Машина:", result["result"]["vehicle_id"])
    print()
    print("Время без кэша:", f"{result['first_time']:.6f}", "сек.")
    print("Время с кэшем:", f"{result['second_time']:.6f}", "сек.")
    print("Ускорение:", f"{result['speedup']:.2f}x")
    print("Cache:", result["cache_info"])
    print()


# =========================
# ЛАБОРАТОРНАЯ №4
# ФУНКЦИОНАЛЬНЫЕ ПАТТЕРНЫ: Maybe / Either
# (сами контейнеры — в containers.py, ЗАДАНИЕ 1)
# =========================

# Типы-алиасы: данные в проекте — кортежи.
# Order = (id_заказа, id_склада, вес_кг, статус)
Order = tuple
Queue = tuple  # кортеж заказов одного склада


class Rule(NamedTuple):
    """Правило валидации заказа: имя, предикат и сообщение об ошибке."""
    name: str
    check: Callable[[Order], bool]
    message: str


# Фабрики правил — замыкания (как by_status / by_wh из Лабы №1).
def min_weight_rule(lo):
    return Rule("min_weight", lambda o: o[2] >= lo, f"вес меньше {lo} кг")


def max_weight_rule(hi):
    return Rule("max_weight", lambda o: o[2] <= hi, f"вес больше {hi} кг")


def allowed_status_rule(statuses):
    return Rule(
        "status",
        lambda o: o[3] in statuses,
        f"недопустимый статус (разрешены: {', '.join(statuses)})"
    )


def warehouse_exists_rule(wh_data):
    wh_ids = frozenset(wh[0] for wh in wh_data)
    return Rule(
        "warehouse",
        lambda o: o[1] in wh_ids,
        "склад не найден"
    )


def default_rules(wh_data, vehicle_data):
    """Стандартный набор правил для пайплайна."""
    max_capacity = max((v[2] for v in vehicle_data), default=0)

    return (
        min_weight_rule(1),
        max_weight_rule(max_capacity),
        allowed_status_rule(("new", "ready")),
        warehouse_exists_rule(wh_data),
    )


# ЗАДАНИЕ 2А. safe_order -> Maybe[Order]
def safe_order(orders_data, oid) -> Maybe:
    """Ищет заказ по id. Нет заказа -> Nothing (а не None / исключение)."""
    return next(
        (Just(o) for o in orders_data if o[0] == oid),
        Nothing()
    )


def _passes(rule, order):
    # Кривые данные (короткий кортеж, не тот тип) = правило не выполнено.
    try:
        return bool(rule.check(order))
    except (IndexError, TypeError):
        return False


# ЗАДАНИЕ 2Б. validate_order -> Either[dict, Order]
def validate_order(o: Order, rules: tuple) -> Either:
    """Проверяет заказ по всем правилам, копит ВСЕ ошибки."""
    errors = tuple(
        rule.message
        for rule in rules
        if not _passes(rule, o)
    )

    if errors:
        order_id = o[0] if isinstance(o, tuple) and o else None
        return Left({"order_id": order_id, "errors": errors})

    return Right(o)


# ЗАДАНИЕ 2В. validate_queue -> Either[dict, Queue]
def validate_queue(q: Queue, rules: tuple) -> Either:
    """Очередь валидна, если она не пуста и каждый заказ прошёл правила."""
    if len(q) == 0:
        return Left({"error": "empty_queue", "failed": {}})

    failed = {
        order[0]: result.error["errors"]
        for order, result in (
            (order, validate_order(order, rules))
            for order in q
        )
        if result.is_left()
    }

    if failed:
        return Left({"error": "invalid_queue", "failed": failed})

    return Right(q)


# ЗАДАНИЕ 3. ПАЙПЛАЙН: заказ -> валидация -> очередь -> маршрут
MAX_BRUTE_FORCE = 8  # больше заказов — полный перебор слишком дорог


def assign_to_queue(order: Order, orders_data) -> Either:
    """Назначение в очередь: очередь = заказы того же склада."""
    queue = build_queue_tree(orders_data, order[1])

    if order not in queue:
        return Left({"error": "order_not_in_queue", "order_id": order[0]})

    return Right(queue)


def plan_route(queue: Queue, wh_data, vehicle_data) -> Either:
    """Планирование маршрута для очереди. Ошибки — через Left."""
    order_ids = get_order_ids(queue)
    total = total_weight(queue)

    missing = tuple(
        order[0] for order in queue
        if get_warehouse(order[1], wh_data) is None
    )
    if missing:
        return Left({"error": "city_not_found", "order_ids": missing})

    if not any(v[3] and v[2] >= total for v in vehicle_data):
        return Left({"error": "no_vehicle", "total_weight": total})

    if len(order_ids) <= MAX_BRUTE_FORCE:
        route = {
            **compute_route(order_ids, wh_data, vehicle_data),
            "method": "brute_force",
            "order_ids": order_ids,
        }
    else:
        ordered = nearest_neighbor_route(order_ids, wh_data)
        distance = route_distance(ordered, wh_data)
        route = {
            "distance": distance,
            "duration": distance // 60,
            "vehicle_id": choose_vehicle(order_ids, vehicle_data)[0],
            "method": "nearest_neighbor",
            "order_ids": ordered,
        }

    return Right(route)


def process_order(oid, orders_data, wh_data, vehicle_data, rules) -> Either:
    """
    Полный пайплайн без единого if/try:
    id -> Maybe[Order] -> Either -> валидация -> очередь
       -> валидация очереди -> маршрут.
    Первая же ошибка проходит по цепочке без изменений (Left).
    """
    return (
        safe_order(orders_data, oid)
        .to_either({"error": "order_not_found", "order_id": oid})
        .bind(lambda order: validate_order(order, rules))
        .bind(lambda order: (
            assign_to_queue(order, orders_data)
            .bind(lambda queue: validate_queue(queue, rules))
            .bind(lambda queue: plan_route(queue, wh_data, vehicle_data))
            .map(lambda route: {"order": order, **route})
        ))
    )


def parse_int(text) -> Maybe:
    """Безопасный разбор числа из ввода: Just(int) или Nothing."""
    try:
        return Just(int(text))
    except (ValueError, TypeError):
        return Nothing()


def error_kind(err) -> str:
    """Короткое название типа ошибки (для группировки в отчёте)."""
    if not isinstance(err, dict):
        return "Другое"
    if err.get("error") == "order_not_found":
        return "Заказ не найден"
    if "errors" in err:
        return "Заказ не прошёл проверку"
    if err.get("error") == "invalid_queue":
        return "В очереди плохой заказ"
    if err.get("error") == "empty_queue":
        return "Пустая очередь"
    if err.get("error") == "no_vehicle":
        return "Нет подходящей машины"
    if err.get("error") == "city_not_found":
        return "Город склада не найден"
    return "Другое"


def format_error(err) -> str:
    """Человекочитаемое сообщение вместо сырого словаря ошибки."""
    if not isinstance(err, dict):
        return str(err)

    kind = err.get("error")

    if kind == "order_not_found":
        return f"заказ {err['order_id']} не найден"
    if "errors" in err:
        return "; ".join(err["errors"])
    if kind == "invalid_queue":
        return "; ".join(
            f"заказ {oid}: {', '.join(msgs)}"
            for oid, msgs in err["failed"].items()
        )
    if kind == "empty_queue":
        return "очередь пуста"
    if kind == "no_vehicle":
        return f"нет машины на {err['total_weight']} кг"
    if kind == "city_not_found":
        return f"нет города склада для заказов {err['order_ids']}"
    return str(err)


def describe_result(result: Either) -> str:
    """Форматирует результат пайплайна для печати."""
    return result.fold(
        lambda err: f"ОШИБКА: {format_error(err)}",
        lambda ok: (
            f"OK: заказ {ok['order'][0]}, очередь {ok['order_ids']}, "
            f"{ok['distance']} км, {ok['duration']} ч, "
            f"машина {ok['vehicle_id']} ({ok['method']})"
        )
    )


# UI / REPORTS: Functional Core
def show_pipeline_report(order_id=None):
    """Reports → Functional Core: пайплайн для одного заказа."""
    rules = default_rules(warehouses, vehicles)
    result = process_order(order_id, orders, warehouses, vehicles, rules)

    print()
    print("╔════════════════════════════════════════════╗")
    print("║ REPORTS · Functional Core: пайплайн заказа ║")
    print("╚════════════════════════════════════════════╝")
    print(f"  Заказ: {order_id}")
    result.fold(
        lambda err: print(f"  ✗ {error_kind(err)}\n    {format_error(err)}"),
        lambda ok: print(
            f"  ✓ Успешно\n"
            f"    Очередь:  {ok['order_ids']}\n"
            f"    Маршрут:  {ok['distance']} км, {ok['duration']} ч\n"
            f"    Машина:   №{ok['vehicle_id']} ({ok['method']})"
        )
    )
    print()


def show_pipeline_summary():
    """Reports → Functional Core: сводка по всем заказам."""
    rules = default_rules(warehouses, vehicles)
    results = tuple(
        (order, process_order(order[0], orders, warehouses, vehicles, rules))
        for order in orders
    )
    ok = tuple(r for r in results if r[1].is_right())
    bad = tuple(r for r in results if r[1].is_left())

    def row(order, result):
        mark, text = result.fold(
            lambda err: ("✗", format_error(err)),
            lambda v: (
                "✓",
                f"очередь {v['order_ids']} · {v['distance']} км · "
                f"машина №{v['vehicle_id']}"
            )
        )
        return (
            f"  {order[0]:>4} │ {order[1]:>5} │ {order[2]:>5} │ "
            f"{order[3]:<10} │ {mark} {text}"
        )

    line = "───────┼───────┼───────┼────────────┼" + "─" * 52

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║ REPORTS · Functional Core: сводка по всем заказам        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("  Заказ │ Склад │   Вес │ Статус     │ Результат")
    print(line)
    for order, result in results:
        print(row(order, result))
    print(line)

    print(f"  ✓ Успешно: {len(ok)}    ✗ С ошибками: {len(bad)}    "
          f"Всего: {len(results)}")

    kinds = {}
    for order, result in bad:
        kind = error_kind(result.error)
        kinds[kind] = kinds.get(kind, ()) + (order[0],)

    if kinds:
        print()
        print("  Ошибки по типам:")
        for kind, ids in kinds.items():
            print(f"   • {kind}: {len(ids)}  (заказы {', '.join(map(str, ids))})")
    print()


def reports_menu():
    while True:
        print()
        print("----- Reports -----")
        print("1. Лучший маршрут (cached)")
        print("2. Functional Core: пайплайн заказа")
        print("3. Functional Core: сводка по всем заказам")
        print("0. Назад")

        choice = input("Выберите: ")

        if choice == "1":
            show_best_route_report()
        elif choice == "2":
            shown = parse_int(input("ID заказа: ")).map(show_pipeline_report)
            if shown.is_nothing():
                print("Нужно ввести целое число.")
        elif choice == "3":
            show_pipeline_summary()
        elif choice == "0":
            break
        else:
            print("Неверный выбор.")


# =========================
# ОСНОВНАЯ ПРОГРАММА
# =========================

if __name__ == "__main__":

    print("======================================")
    print("ЛАБОРАТОРНАЯ РАБОТА №4")
    print("Функциональные паттерны: Maybe / Either")
    print("======================================")

    print()
    print("Количество городов:", len(cities))
    print("Количество складов:", len(warehouses))
    print("Количество заказов:", len(orders))
    print("Количество машин:", len(vehicles))

    print()
    print("Общий вес заказов:", total_weight(orders), "кг")

    ready_filter = by_status("ready")
    ready_orders = filter_orders(orders, ready_filter)
    print("Готовых заказов:", len(ready_orders))

    weight_filter = by_weight_range(500, 800)
    weight_orders = filter_orders(orders, weight_filter)
    print("Заказов весом 500-800 кг:", len(weight_orders))

    warehouse_filter = by_wh(1)
    warehouse_orders = filter_orders(orders, warehouse_filter)
    print("Заказов на складе №1:", len(warehouse_orders))

    print("Город склада №1:", get_warehouse_city(1))

    print()
    print("Маршруты:")
    for route in traverse_routes(routes):
        print("-", route)

    print()
    print("Заказы склада №2:")
    queue_orders = build_queue_tree(orders, 2)

    for order in queue_orders:
        print(
            "ID:", order[0],
            "| Вес:", order[2],
            "| Статус:", order[3]
        )

    reports_menu()

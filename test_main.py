from main import (
    by_status,
    by_weight_range,
    by_wh,
    traverse_routes,
    build_queue_tree,
    get_order_ids,
    nearest_neighbor_route,
    route_distance,
    choose_vehicle,
    compute_route,
    measure_route_cache,
    total_weight,
    filter_orders,
    routes,
    # Лаба №4
    Rule,
    min_weight_rule,
    max_weight_rule,
    allowed_status_rule,
    warehouse_exists_rule,
    default_rules,
    safe_order,
    validate_order,
    validate_queue,
    assign_to_queue,
    plan_route,
    process_order,
    parse_int,
    describe_result,
)

from containers import Just, Nothing, Left, Right

from orders import orders
from warehouses import warehouses
from vehicles import vehicles


# =========================
# ТЕСТЫ ЛАБОРАТОРНОЙ РАБОТЫ №1
# Лямбды, map/filter/reduce, замыкания (тесты 1–6, 11, 11а)
# =========================

# 1. Проверка фильтра по статусу ready
def test_status():
    result = by_status("ready")(
        (1, 1, 500, "ready")
    )
    assert result is True


# 2. Проверка фильтра по статусу new
def test_status_new():
    result = by_status("new")(
        (2, 1, 700, "new")
    )
    assert result is True


# 3. Проверка диапазона веса
def test_weight():
    result = by_weight_range(500, 800)(
        (3, 1, 700, "new")
    )
    assert result is True


# 4. Проверка веса вне диапазона
def test_weight_outside():
    result = by_weight_range(500, 800)(
        (4, 1, 900, "ready")
    )
    assert result is False


# 5. Проверка фильтра по складу
def test_warehouse():
    result = by_wh(2)(
        (5, 2, 600, "ready")
    )
    assert result is True


# 6. Проверка другого склада
def test_warehouse_different():
    result = by_wh(3)(
        (6, 2, 600, "ready")
    )
    assert result is False


# =========================
# ТЕСТЫ ЛАБОРАТОРНОЙ РАБОТЫ №2
# Рекурсия (тесты 7–10, 10а, 10б)
# =========================

# 7. Проверка рекурсивного обхода маршрутов
def test_routes():
    result = traverse_routes(
        (
            "Алматы -> Астана",
            "Астана -> Ташкент"
        )
    )

    assert len(result) == 2
    assert result[0] == "Алматы -> Астана"


# 8. Проверка пустого списка маршрутов
def test_empty_routes():
    result = traverse_routes(())
    assert result == ()


# 9. Проверка рекурсивного построения очереди
def test_queue():
    result = build_queue_tree(
        (
            (1, 1, 500, "new"),
            (2, 2, 600, "ready"),
            (3, 2, 700, "new")
        ),
        2
    )

    assert len(result) == 2


# 10. Проверка очереди для склада без заказов
def test_empty_queue():
    result = build_queue_tree(
        (
            (1, 1, 500, "new"),
            (2, 2, 600, "ready")
        ),
        99
    )

    assert result == ()


# 11. Проверка получения ID заказов
def test_order_ids():
    result = get_order_ids(
        (
            (10, 1, 500, "new"),
            (11, 2, 700, "ready")
        )
    )

    assert result == (10, 11)


# 11а. ЛАБА 1 — сумма весов через reduce + фильтрация по замыканию
def test_total_weight_and_filter():
    data = (
        (1, 1, 500, "new"),
        (2, 1, 700, "ready"),
        (3, 2, 300, "ready"),
    )

    assert total_weight(data) == 1500
    assert total_weight(()) == 0
    assert len(filter_orders(data, by_status("ready"))) == 2


# 10а. ЛАБА 2 — рекурсивный обход всех маршрутов проекта
def test_traverse_all_routes():
    result = traverse_routes(routes)

    assert result == routes
    assert len(result) == 10


# 10б. ЛАБА 2 — очередь склада из реальных данных (рекурсия)
def test_queue_real_data():
    result = build_queue_tree(orders, 1)

    assert get_order_ids(result) == (1, 22)


# =========================
# ТЕСТЫ ЛАБОРАТОРНОЙ РАБОТЫ №3
# =========================

# 12. ЗАДАНИЕ 1А — проверка ближайшего соседа
def test_nearest_neighbor():
    order_ids = (1, 2, 3, 4)
    result = nearest_neighbor_route(order_ids, warehouses)

    assert len(result) == 4
    assert set(result) == set(order_ids)


# 13. ЗАДАНИЕ 1Б — проверка расчёта расстояния
def test_route_distance():
    result = route_distance((1, 2), warehouses)

    assert result == 100


# 14. ЗАДАНИЕ 1 — проверка выбора автомобиля
def test_choose_vehicle():
    result = choose_vehicle((1, 2), vehicles)

    assert result is not None
    assert result[3] is True
    assert result[2] >= 1200


# 15. ЗАДАНИЕ 1 — проверка полной функции маршрута
def test_compute_route():
    order_ids = (1, 2, 3)

    result = compute_route(
        order_ids,
        warehouses,
        vehicles
    )

    assert "distance" in result
    assert "duration" in result
    assert "vehicle_id" in result
    assert result["distance"] >= 0
    assert result["duration"] >= 0


# 16. ЗАДАНИЕ 1В — проверка @lru_cache
def test_compute_route_cache():
    compute_route.cache_clear()

    order_ids = (1, 2, 3, 4, 5)

    compute_route(
        order_ids,
        warehouses,
        vehicles
    )

    first_info = compute_route.cache_info()

    compute_route(
        order_ids,
        warehouses,
        vehicles
    )

    second_info = compute_route.cache_info()

    assert first_info.misses == 1
    assert second_info.hits == 1


# 17. ЗАДАНИЕ 2 — проверка замера производительности
def test_measure_cache():
    result = measure_route_cache(
        (1, 2, 3),
        warehouses,
        vehicles
    )

    assert result["first_time"] >= 0
    assert result["second_time"] >= 0
    assert result["result"]["vehicle_id"] is not None


# =========================
# ТЕСТЫ ЛАБОРАТОРНОЙ РАБОТЫ №4
# Maybe / Either, обёртки, пайплайн
# =========================

RULES = default_rules(warehouses, vehicles)


# 18. ЗАДАНИЕ 1 — Maybe: map/bind/get_or_else
def test_maybe_just_and_nothing():
    assert Just(2).map(lambda x: x * 3) == Just(6)
    assert Just(2).bind(lambda x: Just(x + 1)) == Just(3)
    assert Just(2).filter(lambda x: x > 5) == Nothing()
    assert Nothing().map(lambda x: x * 3) == Nothing()
    assert Nothing().bind(lambda x: Just(x)).is_nothing()
    assert Nothing().get_or_else("default") == "default"
    assert Just(7).get_or_else("default") == 7


# 19. ЗАДАНИЕ 1 — Either: map/bind/short-circuit/fold
def test_either_right_and_left():
    assert Right(2).map(lambda x: x + 1) == Right(3)
    assert Right(2).bind(lambda x: Left("boom")) == Left("boom")
    assert Left("e").map(lambda x: x + 1) == Left("e")
    assert Left("e").bind(lambda x: Right(x)) == Left("e")
    assert Left("e").map_left(str.upper) == Left("E")
    assert Left("e").get_or_else(0) == 0
    assert Right(5).fold(lambda e: "L", lambda v: "R") == "R"
    assert Left(5).fold(lambda e: "L", lambda v: "R") == "L"


# 20. ЗАДАНИЕ 1 — конверсии Maybe <-> Either
def test_maybe_either_conversion():
    assert Just(1).to_either("err") == Right(1)
    assert Nothing().to_either("err") == Left("err")
    assert Right(1).to_maybe() == Just(1)
    assert Left("e").to_maybe() == Nothing()


# 21. ЗАДАНИЕ 2 — safe_order: заказ найден
def test_safe_order_found():
    result = safe_order(orders, 3)

    assert result == Just((3, 3, 300, "new"))


# 22. ЗАДАНИЕ 2 — safe_order: заказа нет -> Nothing, без исключений
def test_safe_order_missing():
    assert safe_order(orders, 999) == Nothing()
    assert safe_order((), 1) == Nothing()
    assert safe_order(orders, 999).get_or_else(None) is None


# 23. ЗАДАНИЕ 2 — validate_order: корректный заказ
def test_validate_order_ok():
    order = (1, 1, 500, "new")

    assert validate_order(order, RULES) == Right(order)


# 24. ЗАДАНИЕ 2 — validate_order: копит все ошибки сразу
def test_validate_order_accumulates_errors():
    bad = (50, 999, 0, "cancelled")
    result = validate_order(bad, RULES)

    assert result.is_left()
    assert result.error["order_id"] == 50
    assert len(result.error["errors"]) == 3  # вес, статус, склад


# 25. ЗАДАНИЕ 2 — validate_order: мусорные данные не роняют программу
def test_validate_order_malformed():
    result = validate_order((7,), RULES)

    assert result.is_left()
    assert result.error["order_id"] == 7


# 26. ЗАДАНИЕ 2 — правила-замыкания
def test_rule_factories():
    assert min_weight_rule(10).check((1, 1, 5, "new")) is False
    assert max_weight_rule(10).check((1, 1, 5, "new")) is True
    assert allowed_status_rule(("new",)).check((1, 1, 5, "ready")) is False
    assert warehouse_exists_rule(warehouses).check((1, 1, 5, "new")) is True
    assert isinstance(min_weight_rule(1), Rule)


# 27. ЗАДАНИЕ 2 — validate_queue: корректная очередь
def test_validate_queue_ok():
    queue = build_queue_tree(orders, 1)

    assert validate_queue(queue, RULES) == Right(queue)


# 28. ЗАДАНИЕ 2 — validate_queue: пустая очередь и плохие заказы
def test_validate_queue_errors():
    empty = validate_queue((), RULES)
    assert empty.error["error"] == "empty_queue"

    queue = (
        (1, 1, 500, "new"),
        (2, 1, 0, "new"),
        (3, 1, 100, "cancelled"),
    )
    result = validate_queue(queue, RULES)

    assert result.is_left()
    assert set(result.error["failed"]) == {2, 3}


# 29. ЗАДАНИЕ 3 — пайплайн: успешный путь
def test_pipeline_success():
    result = process_order(1, orders, warehouses, vehicles, RULES)

    assert result.is_right()
    assert result.value["order"] == (1, 1, 500, "new")
    assert result.value["order_ids"] == (1, 22)
    assert result.value["vehicle_id"] is not None
    assert result.value["distance"] == 0  # оба заказа на складе №1


# 30. ЗАДАНИЕ 3 — пайплайн: заказа нет
def test_pipeline_order_not_found():
    result = process_order(999, orders, warehouses, vehicles, RULES)

    assert result == Left({"error": "order_not_found", "order_id": 999})


# 31. ЗАДАНИЕ 3 — пайплайн: сам заказ не прошёл валидацию
def test_pipeline_invalid_order():
    result = process_order(4, orders, warehouses, vehicles, RULES)

    assert result.is_left()
    assert result.error["order_id"] == 4  # статус processing


# 32. ЗАДАНИЕ 3 — пайплайн: заказ ок, но в очереди плохой заказ
def test_pipeline_invalid_queue():
    result = process_order(3, orders, warehouses, vehicles, RULES)

    # заказ 3 (new) валиден, а заказ 24 из той же очереди — processing
    assert result.is_left()
    assert result.error["error"] == "invalid_queue"
    assert 24 in result.error["failed"]


# 33. ЗАДАНИЕ 3 — assign_to_queue / plan_route по отдельности
def test_assign_and_plan_route():
    order = (1, 1, 500, "new")
    queue = assign_to_queue(order, orders)
    assert queue.value == ((1, 1, 500, "new"), (22, 1, 500, "ready"))

    assert assign_to_queue((999, 1, 1, "new"), orders).is_left()

    heavy = ((1, 1, 1000, "new"), (22, 1, 1000, "ready"))
    no_car = plan_route(heavy, warehouses, vehicles)
    assert no_car.error["error"] == "no_vehicle"

    bad_city = plan_route(((1, 999, 10, "new"),), warehouses, vehicles)
    assert bad_city.is_left()


# 34. Вспомогательное — parse_int и describe_result
def test_parse_int_and_describe():
    assert parse_int("12") == Just(12)
    assert parse_int("abc") == Nothing()
    assert parse_int(None) == Nothing()

    ok = process_order(1, orders, warehouses, vehicles, RULES)
    assert describe_result(ok).startswith("OK")
    assert describe_result(Left("x")).startswith("ОШИБКА")

from main import (
    by_status,
    by_weight_range,
    by_wh,
    traverse_routes,
    build_queue_tree
)


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


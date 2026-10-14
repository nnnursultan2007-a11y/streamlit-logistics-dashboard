import collections

import pandas as pd
import streamlit as st

from cities import cities
from containers import Just, Left, Nothing, Right
from main import (
    allowed_status_rule,
    assign_to_queue,
    build_queue_tree,
    by_status,
    by_weight_range,
    by_wh,
    choose_vehicle,
    compute_route,
    default_rules,
    describe_result,
    error_kind,
    filter_orders,
    format_error,
    get_city_name,
    get_city_id_for_order,
    get_order,
    get_order_ids,
    get_warehouse,
    get_warehouse_city,
    max_weight_rule,
    measure_route_cache,
    min_weight_rule,
    nearest_neighbor_route,
    parse_int,
    plan_route,
    process_order,
    route_distance,
    routes,
    safe_order,
    total_weight,
    traverse_routes,
    validate_order,
    validate_queue,
    warehouse_exists_rule,
)
from orders import orders
from vehicles import vehicles
from warehouses import warehouses


st.set_page_config(page_title="Qamqor Logistics", page_icon="📦", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #f5f7fb; }
    [data-testid="stSidebar"] { background: #101b35; }
    [data-testid="stSidebar"] * { color: #edf3ff !important; }
    .hero { padding: 1.35rem 1.55rem; border-radius: 20px; color: white;
      background: linear-gradient(115deg,#142444 0%,#244b76 58%,#367e83 100%);
      margin: .35rem 0 1.25rem 0; }
    .hero h1 { font-family: Manrope,sans-serif; font-size: 2rem; margin: 0; }
    .hero p { color: #d3e4f2; margin: .35rem 0 0; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #e7ebf2;
      padding: 15px 18px; border-radius: 15px; box-shadow: 0 4px 14px #1a31500a; }
    div[data-testid="stMetricLabel"] { color: #6b7890; }
    .section-note { color:#718096; font-size:.92rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

city_by_id = {city[0]: city for city in cities}
warehouse_by_id = {warehouse[0]: warehouse for warehouse in warehouses}
status_labels = {"new": "Жаңа", "ready": "Дайын", "processing": "Өңделуде"}
rules = default_rules(warehouses, vehicles)


def order_frame(records):
    rows = []
    for order_id, warehouse_id, weight, status in records:
        warehouse = warehouse_by_id.get(warehouse_id)
        city = city_by_id.get(warehouse[2]) if warehouse else None
        rows.append({
            "Тапсырыс №": order_id,
            "Қойма": warehouse[1] if warehouse else f"Қойма №{warehouse_id}",
            "Қала": city[1] if city else "Белгісіз",
            "Салмақ (кг)": weight,
            "Күйі": status_labels.get(status, status),
        })
    return pd.DataFrame(rows)


def pipeline_frame():
    rows = []
    for order in orders:
        result = process_order(order[0], orders, warehouses, vehicles, rules)
        if result.is_right():
            data = result.value
            rows.append({
                "№": order[0], "Қойма": order[1], "Салмақ (кг)": order[2],
                "Күйі": status_labels.get(order[3], order[3]), "Нәтиже": "Дайын",
                "Маршрут (км)": data["distance"], "Көлік №": data["vehicle_id"],
            })
        else:
            rows.append({
                "№": order[0], "Қойма": order[1], "Салмақ (кг)": order[2],
                "Күйі": status_labels.get(order[3], order[3]),
                "Нәтиже": f"{error_kind(result.error)}: {format_error(result.error)}",
                "Маршрут (км)": "—", "Көлік №": "—",
            })
    return pd.DataFrame(rows)


st.sidebar.markdown("## 📦 QAMQOR")
st.sidebar.caption("Логистика басқару панелі")
page = st.sidebar.radio(
    "Бөлім", [
        "Шолу", "Тапсырыстар", "Қоймалар", "Маршруттар", "Көліктер",
        "Маршрутты есептеу", "Functional Core", "Maybe / Either",
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("Зертханалар №1–4 · Python functions")

ready_orders = filter_orders(orders, by_status("ready"))
available_vehicles = [vehicle for vehicle in vehicles if vehicle[3]]
df_orders = order_frame(orders)

st.markdown(
    "<div class='hero'><h1>Логистика бақылау орталығы</h1>"
    "<p>Тапсырыстар, қоймалар және маршрутты жоспарлау бір панельде</p></div>",
    unsafe_allow_html=True,
)

if page == "Шолу":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Барлық тапсырыс", len(orders))
    c2.metric("Жалпы салмақ", f"{total_weight(orders):,} кг")
    c3.metric("Дайын тапсырыс", len(ready_orders))
    c4.metric("Қолжетімді көлік", f"{len(available_vehicles)}/{len(vehicles)}")
    left, right = st.columns([1.1, .9])
    with left:
        st.subheader("Тапсырыстар күйі")
        status_data = collections.Counter(status_labels.get(o[3], o[3]) for o in orders)
        st.bar_chart(pd.Series(status_data, name="Тапсырыс саны"), color="#397f83")
    with right:
        st.subheader("Қойма жүктемесі")
        warehouse_counts = collections.Counter(o[1] for o in orders)
        chart = pd.DataFrame([
            {"Қойма": w[1].replace(" Центральный склад", ""), "Тапсырыс": warehouse_counts[w[0]]}
            for w in warehouses if warehouse_counts[w[0]]
        ]).set_index("Қойма")
        st.bar_chart(chart, color="#5477b8", horizontal=True)
    st.subheader("Соңғы тапсырыстар")
    st.dataframe(df_orders.tail(8), use_container_width=True, hide_index=True)

elif page == "Тапсырыстар":
    st.subheader("Тапсырыстар")
    a, b, c = st.columns(3)
    state_label = a.selectbox("Күйі", ["Барлығы", *status_labels.values()])
    wh_choices = {"Барлық қойма": None, **{f"№{w[0]} · {w[1]}": w[0] for w in warehouses}}
    wh_label = b.selectbox("Қойма", list(wh_choices))
    weight_range = c.slider("Салмақ диапазоны (кг)", 0, 2000, (0, 2000), step=50)
    filtered = orders
    if state_label != "Барлығы":
        state_key = next(key for key, value in status_labels.items() if value == state_label)
        filtered = filter_orders(filtered, by_status(state_key))
    if wh_choices[wh_label] is not None:
        filtered = filter_orders(filtered, by_wh(wh_choices[wh_label]))
    filtered = filter_orders(filtered, by_weight_range(*weight_range))
    st.caption(f"{len(filtered)} тапсырыс · жиынтық салмақ {total_weight(filtered):,} кг")
    st.dataframe(order_frame(filtered), use_container_width=True, hide_index=True, height=480)

elif page == "Қоймалар":
    st.subheader("Қоймалар және кезек")
    selected_wh = st.selectbox("Қойманы таңдаңыз", warehouses, format_func=lambda w: f"№{w[0]} · {w[1]}")
    queue = build_queue_tree(orders, selected_wh[0])
    st.caption(f"Қала: {get_warehouse_city(selected_wh[0])} · Кезектегі тапсырыс: {len(queue)}")
    st.dataframe(order_frame(queue), use_container_width=True, hide_index=True)
    st.markdown("#### Қойма каталогы")
    st.dataframe(pd.DataFrame([
        {"ID": w[0], "Қойма": w[1], "Қала": get_city_name(w[2]), "Тапсырыс": sum(o[1] == w[0] for o in orders)}
        for w in warehouses
    ]), use_container_width=True, hide_index=True)

elif page == "Маршруттар":
    st.subheader("Алдын ала белгіленген маршруттар")
    for index, route in enumerate(traverse_routes(routes), start=1):
        st.write(f"**{index:02}.** {route}")
    st.caption("Бұл тізім main.py ішіндегі traverse_routes() рекурсиясы арқылы алынды.")

elif page == "Көліктер":
    st.subheader("Көлік паркі")
    total, free, capacity = st.columns(3)
    total.metric("Барлық көлік", len(vehicles))
    free.metric("Қолжетімді", len(available_vehicles))
    capacity.metric("Қолжетімді сыйымдылық", f"{sum(v[2] for v in available_vehicles):,} кг")
    st.dataframe(pd.DataFrame([
        {"№": v[0], "Модель": v[1], "Сыйымдылық (кг)": v[2], "Күйі": "Қолжетімді" if v[3] else "Бос емес"}
        for v in vehicles
    ]), use_container_width=True, hide_index=True)

elif page == "Маршрутты есептеу":
    st.subheader("Маршрутты есептеу")
    st.caption("8 тапсырысқа дейін толық перебор, одан көп болса — жақын көрші әдісі қолданылады.")
    selected_ids = st.multiselect(
        "Маршрутқа кіретін тапсырыстар", [o[0] for o in orders], default=[1, 3, 8, 16],
        format_func=lambda oid: f"№{oid} · {get_warehouse_city(get_order(oid)[1])} · {get_order(oid)[2]} кг",
    )
    if not selected_ids:
        st.info("Есептеу үшін кемінде бір тапсырысты таңдаңыз.")
    else:
        ids = tuple(selected_ids)
        chosen_vehicle = choose_vehicle(ids, vehicles)
        if chosen_vehicle is None:
            st.error(f"Таңдалған тапсырыстардың {total_weight(tuple(get_order(i) for i in ids)):,} кг салмағына сай бос көлік жоқ.")
        else:
            if len(ids) <= 8:
                measurement = measure_route_cache(ids, warehouses, vehicles)
                best_route = measurement["result"]["order_ids"] if "order_ids" in measurement["result"] else ids
                # compute_route returns distance/duration/vehicle; enumerate the best path separately for display.
                from itertools import permutations
                best_route = min(permutations(ids), key=lambda route: route_distance(route, warehouses))
                result = measurement["result"]
                method = "Толық перебор"
                m1, m2, m3 = st.columns(3)
                m1.metric("Ең қысқа қашықтық", f"{result['distance']:,} км")
                m2.metric("Шамаланған уақыт", f"{result['duration']} сағ")
                m3.metric("Таңдалған көлік", f"№{result['vehicle_id']}")
                st.caption(f"Кэштің бірінші шақырылуы {measurement['first_time']:.6f} сек · қайталануы {measurement['second_time']:.6f} сек · жылдамдық {measurement['speedup']:.2f}×")
            else:
                best_route = nearest_neighbor_route(ids, warehouses)
                result = {"distance": route_distance(best_route, warehouses), "duration": route_distance(best_route, warehouses) // 60, "vehicle_id": chosen_vehicle[0]}
                method = "Жақын көрші"
                m1, m2, m3 = st.columns(3)
                m1.metric("Қашықтық", f"{result['distance']:,} км")
                m2.metric("Шамаланған уақыт", f"{result['duration']} сағ")
                m3.metric("Таңдалған көлік", f"№{result['vehicle_id']}")
            st.markdown(f"**Әдіс:** {method}")
            st.write(" → ".join(f"№{oid} ({get_warehouse_city(get_order(oid)[1])})" for oid in best_route))
            st.dataframe(order_frame(tuple(get_order(i) for i in best_route)), use_container_width=True, hide_index=True)
            st.dataframe(pd.DataFrame([
                {"Тапсырыс": oid, "Қала ID": get_city_id_for_order(oid, warehouses),
                 "Қойма": get_warehouse(get_order(oid)[1], warehouses)[1]}
                for oid in best_route
            ]), use_container_width=True, hide_index=True)
            st.caption("Оқу есебінде қашықтық қала ID-лерінің айырмасы × 100 км формуласы бойынша алынады.")

elif page == "Functional Core":
    st.subheader("Functional Core · тапсырысты өңдеу")
    raw_id = st.text_input("Тапсырыс ID", value="1")
    parsed_id = parse_int(raw_id)
    if parsed_id.is_nothing():
        st.warning("ID бүтін сан болуы керек.")
    else:
        order_id = parsed_id.get_or_else(None)
        found = safe_order(orders, order_id)
        if found.is_just():
            queue_result = assign_to_queue(found.get_or_else(None), orders)
            if queue_result.is_right():
                st.caption(f"assign_to_queue(...) → {len(queue_result.value)} тапсырыстық қойма кезегі")
        result = process_order(order_id, orders, warehouses, vehicles, rules)
        if result.is_right():
            st.success(describe_result(result))
            detail = result.value
            st.write(f"Кезек: `{detail['order_ids']}` · маршрут: **{detail['distance']} км** · әдіс: {detail['method']}")
        else:
            st.error(f"{error_kind(result.error)} · {format_error(result.error)}")
        with st.expander("Тексерілетін ережелер"):
            st.write(" · ".join(rule.name for rule in rules))
            st.caption("default_rules, safe_order, validate_order, assign_to_queue, validate_queue, plan_route және process_order орындалды.")

    st.markdown("#### Барлық тапсырыстың есебі")
    summary = pipeline_frame()
    successful = int((summary["Нәтиже"] == "Дайын").sum())
    a, b = st.columns(2)
    a.metric("Сәтті өңделді", successful)
    b.metric("Қате/тексеруден өтпеді", len(summary) - successful)
    st.dataframe(summary, use_container_width=True, hide_index=True, height=430)

    queue_wh = st.selectbox("Кезекті бөлек тексеру", warehouses, format_func=lambda w: f"№{w[0]} · {w[1]}", key="validation_wh")
    queue_result = validate_queue(build_queue_tree(orders, queue_wh[0]), rules)
    if queue_result.is_right():
        st.success(f"№{queue_wh[0]} қоймасы кезегі тексеруден өтті ({len(queue_result.value)} тапсырыс).")
    else:
        st.warning(f"Кезек қатесі: {format_error(queue_result.error)}")

    with st.expander("Өз тапсырысыңызды ережемен тексеру"):
        v1, v2, v3 = st.columns(3)
        custom_wh = v1.selectbox("Қойма", warehouses, format_func=lambda w: f"№{w[0]} · {w[1]}", key="custom_validation_wh")
        custom_weight = v2.number_input("Салмақ (кг)", min_value=0, max_value=5000, value=700, step=50, key="custom_validation_weight")
        custom_status = v3.selectbox("Күйі", ["new", "ready", "processing", "cancelled"], key="custom_validation_status")
        low_limit = st.number_input("Ең аз рұқсат салмақ", min_value=0, max_value=5000, value=1, step=1)
        custom_order = (9999, custom_wh[0], custom_weight, custom_status)
        custom_rules = (
            min_weight_rule(low_limit),
            max_weight_rule(max(v[2] for v in vehicles)),
            allowed_status_rule(("new", "ready")),
            warehouse_exists_rule(warehouses),
        )
        checked = validate_order(custom_order, custom_rules)
        if checked.is_right():
            st.success("Тапсырыс барлық ережеден өтті.")
        else:
            st.error(f"{error_kind(checked.error)}: {format_error(checked.error)}")

elif page == "Maybe / Either":
    st.subheader("Maybe / Either контейнерлерін көру")
    st.caption("Maybe бос мәнді қауіпсіз көрсетеді; Either нәтижені немесе қате дерегін алып жүреді.")
    raw_order_id = st.text_input("Ізделетін тапсырыс ID", value="1", key="maybe_order_id")
    parsed = parse_int(raw_order_id)
    threshold = st.slider("Maybe.filter үшін ең аз жүк салмағы", 0, 1500, 500, step=50)
    if parsed.is_nothing():
        maybe_value = Nothing()
        st.warning("parse_int(input) → Nothing(): бүтін сан енгізілмеді.")
    else:
        maybe_value = safe_order(orders, parsed.get_or_else(None))
        st.write(f"safe_order(...) → `{maybe_value}`")
        displayed = maybe_value.map(lambda order: f"№{order[0]} · {order[2]} кг · {status_labels.get(order[3], order[3])}")
        qualified = maybe_value.filter(lambda order: order[2] >= threshold)
        st.write(f"map(...) → `{displayed}`")
        st.write(f"filter(weight ≥ {threshold}) → `{qualified}`")
        st.write(f"get_or_else('Тапсырыс жоқ') → **{maybe_value.map(lambda o: o[0]).get_or_else('Тапсырыс жоқ')}**")
        st.write(f"to_either(...) → `{maybe_value.to_either({'error': 'order_not_found'})}`")

    with st.expander("Maybe әдістерінің бос мәнмен әрекеті"):
        nothing = Nothing()
        st.write(f"Nothing().is_nothing() → **{nothing.is_nothing()}**")
        st.write(f"map / bind / filter бос мәнде → `{nothing.map(str)}` · `{nothing.bind(lambda value: Just(value))}` · `{nothing.filter(bool)}`")
        st.write(f"get_or_else / to_either → `{nothing.get_or_else('Әдепкі мән')}` · `{nothing.to_either('Тапсырыс жоқ')}`")
        st.write(f"Just(5) мысалы → `{Just(5)}`")

    st.markdown("#### Either: пайплайн нәтижесі")
    either_result = process_order(parsed.get_or_else(-1), orders, warehouses, vehicles, rules)
    st.write(f"process_order(...) → `{either_result}`")
    st.write(f"is_right: **{either_result.is_right()}** · is_left: **{either_result.is_left()}**")
    if either_result.is_right():
        st.write(f"map(...) → `{either_result.map(lambda value: value['distance'])}`")
        st.write(f"bind(...) → `{either_result.bind(lambda value: Right(value['order_ids']))}`")
        st.write(f"get_or_else(None) → `{either_result.get_or_else(None)}`")
        st.write(f"fold(...) → **{either_result.fold(lambda err: 'Қате', lambda value: 'Сәтті маршрут')}**")
        st.write(f"to_maybe() → `{either_result.to_maybe()}`")
    else:
        st.write(f"map_left(format_error) → `{either_result.map_left(format_error)}`")
        st.write(f"get_or_else('Қате') → `{either_result.get_or_else('Қате')}`")
        st.write(f"fold(...) → **{either_result.fold(lambda err: format_error(err), lambda value: 'OK')}**")
        st.write(f"to_maybe() → `{either_result.to_maybe()}`")
    with st.expander("Left және Right әдістері"):
        demo_left = Left("Қате үлгісі")
        demo_right = Right(5)
        st.write(f"Left: is_left={demo_left.is_left()}, is_right={demo_left.is_right()}, map={demo_left.map(lambda n: n + 1)}")
        st.write(f"Left.map_left(str.upper) → `{demo_left.map_left(str.upper)}`")
        st.write(f"Right: is_right={demo_right.is_right()}, is_left={demo_right.is_left()}, bind={demo_right.bind(lambda n: Right(n * 2))}")
        st.write(f"Right.fold(...) → `{demo_right.fold(lambda error: 'Қате', lambda value: value)}` · Left.to_maybe() → `{demo_left.to_maybe()}`")


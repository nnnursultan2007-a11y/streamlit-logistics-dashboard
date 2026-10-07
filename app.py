import collections

import pandas as pd
import streamlit as st

from cities import cities
from main import (
    by_status,
    by_weight_range,
    by_wh,
    build_queue_tree,
    filter_orders,
    get_city_name,
    get_order_ids,
    get_warehouse_city,
    routes,
    total_weight,
    traverse_routes,
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

city_names = {city[0]: city[1] for city in cities}
warehouse_by_id = {warehouse[0]: warehouse for warehouse in warehouses}
statuses = {"new": "Жаңа", "ready": "Дайын", "processing": "Өңделуде"}


def order_frame(records):
    rows = []
    for order_id, warehouse_id, weight, status in records:
        warehouse = warehouse_by_id.get(warehouse_id)
        city = city_names.get(warehouse[2], "Белгісіз") if warehouse else "Белгісіз"
        rows.append({
            "Тапсырыс №": order_id,
            "Қойма": warehouse[1] if warehouse else f"Қойма №{warehouse_id}",
            "Қала": city,
            "Салмағы (кг)": weight,
            "Күйі": statuses.get(status, status),
        })
    return pd.DataFrame(rows)


st.sidebar.markdown("## 📦 QAMQOR")
st.sidebar.caption("Логистика басқару панелі")
page = st.sidebar.radio(
    "Бөлім", ["Шолу", "Тапсырыстар", "Қоймалар", "Маршруттар", "Көліктер", "Алгоритмдер"]
)
st.sidebar.markdown("---")
st.sidebar.caption("Зертханалық жұмыс №2 · Lambda · Closure · Recursion")

ready = filter_orders(orders, by_status("ready"))
available = sum(1 for vehicle in vehicles if vehicle[3])
df = order_frame(orders)

st.markdown(
    "<div class='hero'><h1>Логистика бақылау орталығы</h1>"
    "<p>Тапсырыстар, қоймалар және жеткізу желісі бір панельде</p></div>",
    unsafe_allow_html=True,
)

if page == "Шолу":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Барлық тапсырыс", f"{len(orders):,}", "Тіркелген")
    c2.metric("Жалпы жүк салмағы", f"{total_weight(orders):,} кг", "Барлық тапсырыс")
    c3.metric("Дайын тапсырыс", f"{len(ready)}", f"{len(ready) / len(orders):.0%} үлесі")
    c4.metric("Қолдағы көлік", f"{available}/{len(vehicles)}", "Қазір қолжетімді")

    left, right = st.columns([1.15, .85])
    with left:
        st.subheader("Тапсырыс күйі")
        status_counts = collections.Counter(statuses.get(order[3], order[3]) for order in orders)
        st.bar_chart(pd.Series(status_counts, name="Тапсырыс саны"), color="#397f83")
    with right:
        st.subheader("Қоймалар жүктемесі")
        wh_counts = collections.Counter(order[1] for order in orders)
        load = pd.DataFrame([
            {"Қойма": warehouse[1].replace(" Центральный склад", ""), "Тапсырыс": wh_counts[warehouse[0]]}
            for warehouse in warehouses if wh_counts[warehouse[0]]
        ]).set_index("Қойма")
        st.bar_chart(load, color="#5477b8", horizontal=True)
    st.subheader("Соңғы тапсырыстар")
    st.dataframe(df.tail(7).sort_values("Тапсырыс №", ascending=False), use_container_width=True, hide_index=True)

elif page == "Тапсырыстар":
    st.subheader("Тапсырыстар тізімі")
    st.markdown("<p class='section-note'>Күйі, қоймасы және салмақ диапазоны бойынша сүзгілеңіз.</p>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    selected_status = a.selectbox("Күйі", ["Барлығы", *statuses.values()])
    wh_options = {"Барлық қойма": None, **{f"№{w[0]} · {w[1]}": w[0] for w in warehouses}}
    selected_wh_label = b.selectbox("Қойма", list(wh_options))
    weight_range = c.slider("Салмақ аралығы (кг)", 0, 1500, (0, 1500), step=50)
    filtered = orders
    if selected_status != "Барлығы":
        status_key = next(key for key, value in statuses.items() if value == selected_status)
        filtered = filter_orders(filtered, by_status(status_key))
    if wh_options[selected_wh_label] is not None:
        filtered = filter_orders(filtered, by_wh(wh_options[selected_wh_label]))
    filtered = filter_orders(filtered, by_weight_range(*weight_range))
    st.caption(f"Нәтиже: {len(filtered)} тапсырыс · салмағы {sum(o[2] for o in filtered):,} кг")
    st.dataframe(order_frame(filtered), use_container_width=True, hide_index=True, height=470)

elif page == "Қоймалар":
    st.subheader("Қойма бойынша тапсырыстар")
    selected = st.selectbox("Қойманы таңдаңыз", warehouses, format_func=lambda w: f"№{w[0]} · {w[1]}")
    wh_id = selected[0]
    queue = build_queue_tree(orders, wh_id)
    st.markdown(f"### {selected[1]}")
    st.caption(f"Орналасқан қаласы: {get_warehouse_city(wh_id)} · Тапсырыс саны: {len(queue)}")
    st.dataframe(order_frame(queue), use_container_width=True, hide_index=True)
    counts = collections.Counter(order[1] for order in orders)
    overview = pd.DataFrame([
        {"Қойма №": w[0], "Қойма атауы": w[1], "Қала": city_names.get(w[2], "Белгісіз"), "Тапсырыс": counts[w[0]]}
        for w in warehouses
    ])
    with st.expander("Барлық қойманың жүктемесі"):
        st.dataframe(overview, use_container_width=True, hide_index=True)

elif page == "Маршруттар":
    st.subheader("Жеткізу маршруттары")
    st.caption("Маршруттар main.py ішіндегі traverse_routes() рекурсивті функциясынан алынды.")
    route_list = traverse_routes(routes)
    for idx, route in enumerate(route_list, start=1):
        origin, destination = route.split(" -> ")
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:14px;background:white;padding:13px 17px;"
            f"margin:7px 0;border:1px solid #e7ebf2;border-radius:13px'>"
            f"<span style='color:#397f83;font-weight:700;width:34px'>{idx:02}</span>"
            f"<b>{origin}</b><span style='color:#91a0b5'>──────➜</span><b>{destination}</b></div>",
            unsafe_allow_html=True,
        )

elif page == "Көліктер":
    st.subheader("Көлік паркі")
    vdf = pd.DataFrame([
        {"№": v[0], "Модель": v[1], "Жүк дағдысы (кг)": v[2], "Күйі": "Қолжетімді" if v[3] else "Жолда / бос емес"}
        for v in vehicles
    ])
    total, free, capacity = st.columns(3)
    total.metric("Көлік саны", len(vehicles))
    free.metric("Қолжетімді", available)
    capacity.metric("Қолжетімді жүк сыйымдылығы", f"{sum(v[2] for v in vehicles if v[3]):,} кг")
    st.dataframe(vdf, use_container_width=True, hide_index=True)
    st.subheader("Модель бойынша саны")
    st.bar_chart(vdf.groupby("Модель").size().rename("Көлік саны"), color="#397f83")

else:
    st.subheader("Функцияларды байқап көру")
    st.caption("Төмендегі бөлімдер жүктеген main.py файлындағы функцияларды тікелей іске қосады.")

    lambda_tab, closure_tab, recursion_tab, city_tab = st.tabs(
        ["Lambda және reduce", "Closure және сүзгі", "Рекурсия", "Қаланы іздеу"]
    )

    with lambda_tab:
        weight_col, id_col = st.columns(2)
        weight_col.metric("total_weight(orders)", f"{total_weight(orders):,} кг")
        order_ids = get_order_ids(orders)
        id_col.metric("get_order_ids(orders)", f"{len(order_ids)} ID")
        st.code(f"ID тізімі: {order_ids}", language="python")
        st.caption("Lambda map арқылы салмақ пен ID алады, ал reduce жалпы салмақты қосады.")

    with closure_tab:
        status_labels = {"Жаңа": "new", "Дайын": "ready", "Өңделуде": "processing"}
        status_col, wh_col = st.columns(2)
        chosen_status_label = status_col.selectbox("Күй бойынша (by_status)", list(status_labels))
        chosen_wh = wh_col.selectbox(
            "Қойма бойынша (by_wh)", warehouses,
            format_func=lambda w: f"№{w[0]} · {w[1]}",
        )
        weight_col, max_col = st.columns(2)
        min_weight = weight_col.number_input("Ең аз салмақ (кг)", min_value=0, max_value=5000, value=500, step=50)
        max_weight = max_col.number_input("Ең көп салмақ (кг)", min_value=0, max_value=5000, value=800, step=50)
        if min_weight > max_weight:
            st.warning("Ең аз салмақ ең көп салмақтан үлкен болмауы керек.")
            filtered = ()
        else:
            filtered = filter_orders(orders, by_status(status_labels[chosen_status_label]))
            filtered = filter_orders(filtered, by_weight_range(min_weight, max_weight))
            filtered = filter_orders(filtered, by_wh(chosen_wh[0]))
        st.caption(
            f"filter_orders + үш closure нәтижесі: {len(filtered)} тапсырыс · "
            f"{sum(order[2] for order in filtered):,} кг"
        )
        st.dataframe(order_frame(filtered), use_container_width=True, hide_index=True)
        st.code("by_status(status) · by_weight_range(lo, hi) · by_wh(wh_id) · filter_orders(orders, predicate)", language="python")

    with recursion_tab:
        route_count = len(traverse_routes(routes))
        st.metric("traverse_routes(routes)", f"{route_count} маршрут")
        for index, route in enumerate(traverse_routes(routes), start=1):
            st.write(f"**{index:02}.** {route}")
        st.markdown("---")
        queue_wh = st.selectbox(
            "Кезекті құратын қойма (build_queue_tree)", warehouses,
            format_func=lambda w: f"№{w[0]} · {w[1]}", key="queue_warehouse",
        )
        queue = build_queue_tree(orders, queue_wh[0])
        st.caption(f"Қайтарылған кезек: {len(queue)} тапсырыс · {get_warehouse_city(queue_wh[0])}")
        st.dataframe(order_frame(queue), use_container_width=True, hide_index=True)

    with city_tab:
        city_col, warehouse_col = st.columns(2)
        selected_city = city_col.selectbox(
            "Қала ID-ін таңдаңыз (get_city_name)", cities,
            format_func=lambda city: f"№{city[0]} · {city[1]} ({city[2]})",
        )
        city_col.success(f"get_city_name({selected_city[0]}) → {get_city_name(selected_city[0])}")
        selected_city_wh = warehouse_col.selectbox(
            "Қойманы таңдаңыз (get_warehouse_city)", warehouses,
            format_func=lambda w: f"№{w[0]} · {w[1]}", key="city_warehouse",
        )
        warehouse_col.success(
            f"get_warehouse_city({selected_city_wh[0]}) → {get_warehouse_city(selected_city_wh[0])}"
        )

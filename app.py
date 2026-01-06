import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Кондитерская Учет", layout="centered")
st.title("🍰 Система заказов")

# 1. Подключение
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Пытаемся прочитать лист Inventory
    inventory = conn.read(worksheet="Inventory")
    st.success("Соединение с таблицей установлено!")
except Exception as e:
    st.error("❌ ОШИБКА ПОДКЛЮЧЕНИЯ:")
    st.write("1. Проверь, что внизу таблицы лист называется именно **Inventory**")
    st.write("2. Проверь, что доступ открыт: 'Все, у кого есть ссылка — Редактор'")
    st.write(f"Техническая ошибка: {e}")
    st.stop()

# 2. Проверка колонок
if "Название" not in inventory.columns or "Норма_запаса" not in inventory.columns:
    st.error("❌ ОШИБКА В ТАБЛИЦЕ:")
    st.write("В листе **Inventory** должны быть заголовки в первой строке: **Название** и **Норма_запаса**")
    st.write(f"Сейчас я вижу колонки: {list(inventory.columns)}")
    st.stop()

# 3. Интерфейс
with st.form("input_form"):
    dessert = st.selectbox("Выберите десерт", inventory["Название"].dropna().unique())
    leftover = st.number_input("Остаток вечером (шт)", min_value=0, step=1)
    submit = st.form_submit_button("Рассчитать заказ")

if submit:
    try:
        target = inventory.loc[inventory["Название"] == dessert, "Норма_запаса"].values[0]
        to_order = int(target - leftover) if target > leftover else 0
        
        # Запись в лист Sales
        new_row = pd.DataFrame([{
            "Дата": datetime.now().strftime("%d.%m.%Y"),
            "Название": dessert,
            "Остаток_вечер": leftover,
            "Заказать": to_order
        }])
        
        sales_df = conn.read(worksheet="Sales")
        updated_sales = pd.concat([sales_df, new_row], ignore_index=True)
        conn.update(worksheet="Sales", data=updated_sales)
        
        st.balloons()
        st.success(f"Записано! Нужно заказать: {to_order} шт.")
    except Exception as e:
        st.error(f"Ошибка при сохранении: {e}")
        st.info("Проверь, создан ли второй лист с названием **Sales**")

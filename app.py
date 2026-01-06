import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Кондитерская Учет", layout="centered")

st.title("🍰 Система заказов десертов")

# Подключение к таблице
conn = st.connection("gsheets", type=GSheetsConnection)

# Читаем данные
try:
    inventory = conn.read(worksheet="Inventory")
except Exception as e:
    st.error("Ошибка подключения к таблице. Проверьте ссылку в Secrets.")
    st.stop()

st.subheader("Заполните остатки на вечер")

# Форма ввода
with st.form("input_form"):
    dessert = st.selectbox("Выберите десерт", inventory["Название"].tolist())
    leftover = st.number_input("Сколько осталось в витрине (шт)?", min_value=0, step=1)
    
    submit = st.form_submit_button("Рассчитать заказ")

if submit:
    # Расчет
    target = inventory.loc[inventory["Название"] == dessert, "Норма_запаса"].values[0]
    to_order = int(target - leftover)
    if to_order < 0: to_order = 0
    
    st.info(f"Для '{dessert}' норма {target} шт. Нужно дозаказать: **{to_order} шт.**")
    
    # Подготовка данных для записи
    new_row = pd.DataFrame([{
        "Дата": datetime.now().strftime("%d.%m.%Y"),
        "Название": dessert,
        "Остаток_вечер": leftover,
        "Заказать": to_order
    }])
    
    # Читаем текущие продажи, добавляем новую строку и сохраняем
    sales_df = conn.read(worksheet="Sales")
    updated_sales = pd.concat([sales_df, new_row], ignore_index=True)
    conn.update(worksheet="Sales", data=updated_sales)
    
    st.success("Данные успешно сохранены в Google Таблицу!")

# Кнопка формирования заявки (Excel)
st.divider()
st.subheader("Скачать заявку на завтра")
current_sales = conn.read(worksheet="Sales")
if not current_sales.empty:
    csv = current_sales.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Скачать отчет (CSV)",
        data=csv,
        file_name=f"zayavka_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Кондитерская Учет", layout="centered", page_icon="🍰")
st.title("🍰 Система заказов")

# Ссылка на твою таблицу (CSV экспорт первого листа)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1esisqKI9bcqwo7ZtSNKmBMx9hY5RsPgiWO_ThRH250M/export?format=csv&gid=0"

# Инициализация корзины заказа в памяти браузера
if 'order_list' not in st.session_state:
    st.session_state.order_list = []

# 1. Загрузка данных
try:
    inventory = pd.read_csv(SHEET_URL)
    st.sidebar.success("Склад на связи ✅")
except:
    st.error("Ошибка обновления данных из Google")
    st.stop()

# 2. Форма ввода данных
with st.container():
    st.subheader("📝 Ввод остатков")
    col1, col2 = st.columns(2)
    
    with col1:
        dessert = st.selectbox("Выберите десерт", inventory["Название"].unique())
    with col2:
        leftover = st.number_input("Остаток (шт)", min_value=0, step=1)

    if st.button("Добавить в список"):
        target = inventory.loc[inventory["Название"] == dessert, "Норма_запаса"].values[0]
        to_order = int(target - leftover) if target > leftover else 0
        
        # Добавляем в список в памяти
        st.session_state.order_list.append({
            "Дата": datetime.now().strftime("%d.%m.%Y"),
            "Десерт": dessert,
            "Остаток": leftover,
            "Заказать": to_order
        })
        st.toast(f"Добавлено: {dessert}")

# 3. Отображение текущего черновика заказа
if st.session_state.order_list:
    st.divider()
    st.subheader("🛒 Текущая заявка")
    df_order = pd.DataFrame(st.session_state.order_list)
    st.table(df_order)
    
    if st.button("Очистить список"):
        st.session_state.order_list = []
        st.rerun()

    # 4. Скачивание файла
    csv_data = df_order.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Скачать заявку в Excel (CSV)",
        data=csv_data,
        file_name=f"zakaz_{datetime.now().strftime('%d_%m')}.csv",
        mime="text/csv"
    )

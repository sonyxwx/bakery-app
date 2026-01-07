import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Кондитерская Учет", layout="centered", page_icon="🍰")

st.title("🍰 Система заказов и учета")

# 1. Твои ссылки
# Ссылка на чтение таблицы (лист Inventory)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1esisqKI9bcqwo7ZtSNKmBMx9hY5RsPgiWO_ThRH250M/export?format=csv&gid=0"

# Ссылка на отправку данных в Google Форму
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfEY-HlCXmE0LnTd3Zvp-u5Esjg-h9USuPelJjRc0pXc3WcIg/formResponse"

# 2. Загрузка списка десертов
try:
    inventory = pd.read_csv(SHEET_URL)
    # Очистка данных от пустых строк
    inventory = inventory.dropna(subset=['Название'])
except Exception as e:
    st.error(f"Ошибка загрузки базы данных: {e}")
    st.stop()

# 3. Интерфейс программы
st.subheader("Ввод остатков на вечер")

with st.form("bakery_form", clear_on_submit=True):
    dessert = st.selectbox("Выберите десерт", inventory["Название"].tolist())
    leftover = st.number_input("Сколько штук осталось?", min_value=0, step=1)
    
    submitted = st.form_submit_button("✅ Сохранить и рассчитать")

if submitted:
    # Ищем норму запаса для выбранного десерта
    try:
        target = inventory.loc[inventory["Название"] == dessert, "Норма_запаса"].values[0]
        to_order = int(target - leftover) if target > leftover else 0
        
        # Подготовка данных для отправки в Google Форму
        form_data = {
            "entry.979173601": dessert,      # Название
            "entry.1913568263": str(leftover), # Остаток
            "entry.1313809346": str(to_order)  # Сколько заказать
        }
        
        # Отправка запроса
        response = requests.post(FORM_URL, data=form_data)
        
        if response.status_code == 200:
            st.balloons()
            st.success(f"Данные сохранены!")
            st.info(f"Для '{dessert}' норма {target} шт. Нужно заказать на завтра: **{to_order} шт.**")
        else:
            st.error("Ошибка при сохранении в таблицу. Проверьте настройки формы.")
            
    except Exception as e:
        st.error(f"Произошла ошибка: {e}")

st.divider()
st.caption("Данные автоматически улетают в вашу Google Таблицу (лист 'Ответы на форму')")

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
if submitted:
    try:
        # Берем значение и принудительно превращаем в число (float), чтобы избежать ошибки
        target_raw = inventory.loc[inventory["Название"] == dessert, "Норма_запаса"].values[0]
        target = float(target_raw) 
        
        # Считаем разницу
        to_order = int(target - leftover) if target > leftover else 0
        
        # Подготовка данных для отправки в Google Форму
        form_data = {
            "entry.979173601": dessert,      
            "entry.1913568263": str(leftover), 
            "entry.1313809346": str(to_order)  
        }
        
        # Отправка запроса
        response = requests.post(FORM_URL, data=form_data)
        
        if response.status_code == 200:
            st.balloons()
            st.success(f"Данные сохранены!")
            st.info(f"Для '{dessert}' норма {int(target)} шт. Нужно заказать на завтра: **{to_order} шт.**")
        else:
            st.error("Ошибка при сохранении в таблицу.")
            
    except Exception as e:
        st.error(f"Произошла ошибка: {e}")

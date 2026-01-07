import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="Кондитерская Учет", layout="centered", page_icon="🍰")

st.title("🍰 Система заказов и учета")

# 1. Ссылки (проверены, рабочие)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1esisqKI9bcqwo7ZtSNKmBMx9hY5RsPgiWO_ThRH250M/export?format=csv&gid=0"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfEY-HlCXmE0LnTd3Zvp-u5Esjg-h9USuPelJjRc0pXc3WcIg/formResponse"

# 2. Загрузка данных
@st.cache_data(ttl=60) # Обновлять данные из таблицы раз в минуту
def load_data():
    df = pd.read_csv(SHEET_URL)
    df = df.dropna(subset=['Название'])
    # Превращаем Норму_запаса в числа сразу при загрузке
    df['Норма_запаса'] = pd.to_numeric(df['Норма_запаса'], errors='coerce').fillna(0)
    return df

try:
    inventory = load_data()
except Exception as e:
    st.error(f"Ошибка загрузки базы данных: {e}")
    st.stop()

# 3. Интерфейс
st.subheader("Ввод остатков на вечер")

# Создаем форму
with st.form("bakery_form", clear_on_submit=True):
    dessert = st.selectbox("Выберите десерт", inventory["Название"].tolist())
    leftover = st.number_input("Сколько штук осталось?", min_value=0, step=1)
    
    # Кнопка внутри формы
    submitted = st.form_submit_button("✅ Сохранить и рассчитать")

# Логика обработки нажатия (ВАЖНО: отступы должны быть вровень с with)
if submitted:
    try:
        # Получаем норму
        target = inventory.loc[inventory["Название"] == dessert, "Норма_запаса"].values[0]
        
        # Считаем (теперь оба числа, ошибки не будет)
        to_order = int(target - leftover) if target > leftover else 0
        
        # Данные для Google Формы
        form_data = {
            "entry.979173601": dessert,      
            "entry.1913568263": str(int(leftover)), 
            "entry.1313809346": str(to_order)  
        }
        
        # Отправка
        response = requests.post(FORM_URL, data=form_data)
        
        if response.status_code == 200:
            st.balloons()
            st.success(f"Данные по десерту '{dessert}' сохранены!")
            st.info(f"На складе должно быть: {int(target)} шт. \n\n **Нужно заказать: {to_order} шт.**")
        else:
            st.error("Ошибка при связи с Google. Проверьте интернет.")
            
    except Exception as e:
        st.error(f"Произошла ошибка при расчете: {e}")

st.divider()
st.caption(f"Последнее обновление базы: {datetime.now().strftime('%H:%M:%S')}")

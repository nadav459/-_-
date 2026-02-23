import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.message import EmailMessage
import io
from bidi.algorithm import get_display

COORDS = {
    "heb_month": (1125, 1107.5),
    "heb_date": (1748, 1107.5),
    "eng_month": (1076, 1243),
    "eng_date": (1762, 1243),
    "id_num": (1419, 2145),
    "first_name": (2064, 2145),
    "last_name": (2615, 2145),
    "personal_num": (3514, 2145),
    "enlistment_date": (2849, 2591),
    "service_start": (1760, 3562),
    "service_end": (2602, 3562)
}

def send_log_email(person_name):
    msg = EmailMessage()
    msg.set_content(f"נוצר אישור חדש במערכת עבור: {person_name}")
    msg['Subject'] = f"דיווח מערכת: הופק טופס עבור {person_name}"
    msg['From'] = st.secrets["EMAIL_USER"]
    msg['To'] = st.secrets["ADMIN_EMAIL"]

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
            smtp.send_message(msg)
    except Exception as e:
        st.error(f"שגיאה בשליחת המייל: {e}")

st.set_page_config(page_title="מחולל אישורים", layout="centered")
st.title("מערכת הפקת אישורים מהירה")
# הזרקת עיצוב CSS מותאם אישית
    st.markdown("""
        <style>
        /* עיצוב רקע האפליקציה */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* עיצוב כפתור היצירה */
        div.stButton > button:first-child {
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            width: 100%; /* כפתור לכל הרוחב */
            transition: all 0.3s;
        }
        
        /* אפקט מעבר עכבר (Hover) על הכפתור */
        div.stButton > button:first-child:hover {
            background-color: #1a252f;
            color: #f1c40f; /* צבע צהוב במעבר עכבר */
        }
        
        /* עיצוב תיבות הטקסט */
        .stTextInput > div > div > input {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        }
        </style>
    """, unsafe_allow_html=True)

with st.form("data_form"):
    col1, col2 = st.columns(2)
    with col1:
        last_name = st.text_input("שם משפחה")
        first_name = st.text_input("שם פרטי")
        id_num = st.text_input("תעודת זהות")
        personal_num = st.text_input("מספר אישי")
    with col2:
        heb_date = st.text_input("תאריך עברי (יום)")
        heb_month = st.text_input("חודש עברי")
        eng_date = st.text_input("תאריך לועזי (יום)")
        eng_month = st.text_input("חודש לועזי")
    
    enlistment = st.text_input("תאריך גיוס (למשל 01/01/2020)")
    
    st.write("---")
    st.write("טבלת שירות")
    c3, c4 = st.columns(2)
    with c3:
        service_start = st.text_input("תחילת שירות")
    with c4:
        service_end = st.text_input("סיום שירות")

    submit = st.form_submit_button("צור קובץ והורד")

if submit:
    try:
        # פתיחת תמונת המקור החדשה
        img = Image.open("original.jpg")
        draw = ImageDraw.Draw(img)
        
        # טעינת שני הפונטים בגדלים כפולים מהקודמים
        font_david = ImageFont.truetype("DavidLibre-Medium.ttf", 110)
        font_november = ImageFont.truetype("NovemberSuiteHebrewVF-instanceRegular.ttf", 96)
        
        data_map = {
            "heb_month": heb_month, "heb_date": heb_date,
            "eng_month": eng_month, "eng_date": eng_date,
            "id_num": id_num, "first_name": first_name,
            "last_name": last_name, "personal_num": personal_num,
            "enlistment_date": enlistment,
            "service_start": service_start, "service_end": service_end
        }

        # רשימת השדות שצריכים לקבל את פונט דוד
        david_fields = ["heb_month", "heb_date", "eng_month", "eng_date"]

        for key, text in data_map.items():
            if text: # מוודא שהוכנס טקסט לפני שמציירים
                # בחירת הפונט המתאים לפי שם השדה
                current_font = font_david if key in david_fields else font_november
                
                # *** התיקון הקריטי: הפיכת הטקסט לעברית תקינה משמאל לימין ***
                correct_text = get_display(text)
                
                draw.text(COORDS[key], correct_text, fill="black", font=current_font, anchor="mm")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        file_name = f"{last_name}_{first_name}.png"

        st.success(f"הקובץ עבור {first_name} {last_name} מוכן!")
        
        st.download_button(
            label="לחץ כאן להורדת הקובץ",
            data=byte_im,
            file_name=file_name,
            mime="image/png"
        )

        send_log_email(f"{last_name} {first_name}")
        
    except FileNotFoundError as e:
        st.error(f"שגיאה: חסר קובץ. נא לוודא שקובץ התמונה והפונטים נמצאים בתיקייה. פרטים: {e}")
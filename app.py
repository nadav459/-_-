import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.message import EmailMessage
import io

# הגדרות קבועות - קואורדינטות (הממוצעים שחישבנו)
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
    # כאן תצטרך להגדיר Secrets ב-Streamlit Cloud עבור המייל והסיסמה
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

# שדות קלט למשתמש (השותף)
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
    # 1. פתיחת תמונת המקור (תוודא שהקובץ נמצא בתיקייה)
    try:
        img = Image.open("template.png")
        draw = ImageDraw.Draw(img)
        
        # 2. טעינת פונט (תוודא שקובץ ה-ttf נמצא בתיקייה)
        font = ImageFont.truetype("assistant.ttf", 45) 

        # 3. הכנת הנתונים לכתיבה
        data_map = {
            "heb_month": heb_month, "heb_date": heb_date,
            "eng_month": eng_month, "eng_date": eng_date,
            "id_num": id_num, "first_name": first_name,
            "last_name": last_name, "personal_num": personal_num,
            "enlistment_date": enlistment,
            "service_start": service_start, "service_end": service_end
        }

        # 4. כתיבה על התמונה
        for key, text in data_map.items():
            draw.text(COORDS[key], text, fill="black", font=font, anchor="mm") # anchor="mm" עוזר למרכז לפי הקואורדינטה

        # 5. שמירה לזיכרון לצורך הורדה
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # 6. יצירת שם הקובץ לפי הפורמט שביקשת
        file_name = f"{last_name}_{first_name}.png"

        st.success(f"הקובץ עבור {first_name} {last_name} מוכן!")
        
        st.download_button(
            label="לחץ כאן להורדת הקובץ",
            data=byte_im,
            file_name=file_name,
            mime="image/png"
        )

        # 7. שליחת דיווח למייל
        send_log_email(f"{last_name} {first_name}")
        
    except FileNotFoundError:
        st.error("חסר קובץ מקור (template.png) או פונט (assistant.ttf)")
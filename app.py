import streamlit as st
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import date
from email.utils import formataddr

# ================== SECRETS ==================
st.title("📄 Générateur SK")

compte = st.selectbox("Choisis le compte", ["Compte 1", "Compte 2"])

if compte == "Compte 1":
    api_key = st.secrets["craftmypdf"]["api_key1"]
    template_id = st.secrets["craftmypdf"]["template_id1"]
else:
    api_key = st.secrets["craftmypdf"]["api_key2"]
    template_id = st.secrets["craftmypdf"]["template_id2"]

SMTP_HOST = st.secrets["smtp"]["host"]
SMTP_PORT = st.secrets["smtp"]["port"]
SMTP_USER = st.secrets["smtp"]["user"]
SMTP_PASS = st.secrets["smtp"]["password"]

VAR_NOM = "nom_client"
VAR_EMAIL = "email_client"
VAR_NUMERO = "numero_facture"
VAR_MONTANT = "montant"
VAR_MONTANT_TOTAL = "montant_total"
VAR_TEL = "telephone"
VAR_ADRESSE = "adresse_client"
VAR_DESCRIPTION = "description"
VAR_DATE = "date"

col1, col2 = st.columns(2)
with col1:
    nom = st.text_input("Nom du client *", key="nom")
    email_client = st.text_input("Mensualités *", key="email_client")
    numero = st.text_input("Durée(Mois) *", key="numero")
    montant = st.text_input("Montant du prêt *", key="montant")
    montant_total = st.text_input("Total Mensualités *", key="montant_total")

with col2:
    tel = st.text_input("IBAN (facultatif)", key="tel")
    adresse = st.text_input("Adresse du client (facultatif)", key="adresse")
    description = st.text_input("Téléphone (facultatif)", key="description")

to_email = st.text_input("Destinataire de l'email *", key="to_email")

today = date.today().strftime("%d/%m/%Y")
st.info(f"📅 Date utilisée: **{today}** (DD/MM/RRRR)")

if st.button("🚀 Générer PDF + Envoyer e-mail", type="primary", use_container_width=True):
    if not (nom and email_client and numero and montant and montant_total and to_email):
        st.error("❌ Les champs marqués * sont obligatoires !")
    else:
        data = {
            VAR_NOM: nom.strip(),
            VAR_EMAIL: email_client.strip(),
            VAR_NUMERO: numero.strip(),
            VAR_MONTANT: montant.strip(),
            VAR_MONTANT_TOTAL: montant_total.strip(),
            VAR_TEL: tel.strip(),
            VAR_ADRESSE: adresse.strip(),
            VAR_DESCRIPTION: description.strip(),
            VAR_DATE: today
        }

        with st.spinner("Génération du PDF en cours..."):
            url = "https://api.craftmypdf.com/v1/create"
            payload = {
                "template_id": template_id,
                "data": data,
                "export_type": "file",
                "output_file": "docmnt.pdf"
            }
            headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                pdf_bytes = response.content

                msg = MIMEMultipart()
                msg['From'] = formataddr(("KRD EXPRESS", SMTP_USER))
                msg['To'] = to_email
                msg['Subject'] = "RE: Ponuka úveru"
                msg.attach(MIMEText(
                    "Dobrý deň,\n\nV prílohe nájdete vašu úverovú zmluvu. Prečítajte si ju, podpíšte a vráťte nám ju.\n"
                    "Ak nemáte tlačiareň, vezmite papier, podpíšte ho, napíšte dnešný dátum a vaše meno a priezvisko "
                    "a pošlite nám fotografiu tohto listu.\n\nS pozdravom,",
                    'plain'
                ))

                attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
                attachment.add_header('Content-Disposition', 'attachment', filename="zmluva.pdf")
                msg.attach(attachment)

                server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
                server.quit()

                st.success(f"✅ PDF généré et email envoyé à **{to_email}** !")
                st.balloons()
            else:
                st.error(f"Chyba CraftMyPDF: {response.text}")

# backend/notifier.py  –  Real Email (Gmail SMTP) + SMS (Twilio) engine
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText

# ── credentials from environment variables ────────────────────────────────────
SMTP_HOST  = "smtp.gmail.com"
SMTP_PORT  = 587
SMTP_USER  = os.getenv("BOOTHIQ_EMAIL",    "your_gmail@gmail.com")
SMTP_PASS  = os.getenv("BOOTHIQ_EMAIL_PWD","your_app_password")
FROM_NAME  = "BoothIQ Civic Platform"

TWILIO_SID   = os.getenv("TWILIO_ACCOUNT_SID","")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN","")
TWILIO_FROM  = os.getenv("TWILIO_FROM_NUMBER","")

TYPE_COLORS = {
    "📢 General Announcement":"#3b82f6","🏗️ Development Update":"#f59e0b",
    "📋 Scheme Alert":"#10b981","🗳️ Election Reminder":"#8b5cf6",
    "🚨 Emergency Alert":"#ef4444","💧 Infrastructure Update":"#06b6d4",
}

# ── HTML email builder ────────────────────────────────────────────────────────
def _html_email(voter, title, body, notif_type, priority, link=""):
    nc = TYPE_COLORS.get(notif_type,"#3b82f6")
    pc = {"Low":"#22d3ee","Normal":"#3b82f6","High":"#f59e0b","Urgent":"#ef4444"}.get(priority,"#3b82f6")
    link_html = (f'<p style="margin-top:14px;"><a href="{link}" '
                 f'style="color:{nc};font-size:13px;">🔗 {link}</a></p>') if link else ""
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:28px 16px;">
    <table width="600" cellpadding="0" cellspacing="0"
           style="background:#ffffff;border-radius:14px;overflow:hidden;
                  box-shadow:0 4px 20px rgba(0,0,0,.10);">
      <tr><td style="background:{nc};padding:22px 28px;">
        <table width="100%" cellpadding="0" cellspacing="0"><tr>
          <td>
            <div style="font-size:10px;color:rgba(255,255,255,.75);letter-spacing:2px;
                        text-transform:uppercase;margin-bottom:4px;">{notif_type}</div>
            <div style="font-size:20px;font-weight:700;color:#fff;line-height:1.3;">{title}</div>
          </td>
          <td align="right" valign="top">
            <span style="background:rgba(255,255,255,.2);color:#fff;padding:4px 12px;
                         border-radius:20px;font-size:11px;font-weight:600;">{priority}</span>
          </td>
        </tr></table>
      </td></tr>
      <tr><td style="padding:24px 28px 0;">
        <p style="margin:0;font-size:15px;color:#1e293b;">Dear <strong>{voter['name']}</strong>,</p>
      </td></tr>
      <tr><td style="padding:14px 28px 0;">
        <p style="margin:0;font-size:14px;color:#334155;line-height:1.7;">{body}</p>
        {link_html}
      </td></tr>
      <tr><td style="padding:20px 28px;">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#f8fafc;border-radius:8px;padding:12px;border:1px solid #e2e8f0;">
          <tr>
            <td style="font-size:10px;color:#94a3b8;padding:2px 8px;">VOTER ID</td>
            <td style="font-size:10px;color:#94a3b8;padding:2px 8px;">BOOTH</td>
            <td style="font-size:10px;color:#94a3b8;padding:2px 8px;">OCCUPATION</td>
          </tr>
          <tr>
            <td style="font-size:13px;font-weight:600;color:#1e293b;padding:2px 8px;">{voter['voter_id']}</td>
            <td style="font-size:13px;font-weight:600;color:#1e293b;padding:2px 8px;">{voter['booth_id']}</td>
            <td style="font-size:13px;font-weight:600;color:#1e293b;padding:2px 8px;">{voter['occupation']}</td>
          </tr>
        </table>
      </td></tr>
      <tr><td style="background:#f8fafc;padding:14px 28px;border-top:1px solid #e2e8f0;">
        <p style="margin:0;font-size:11px;color:#94a3b8;text-align:center;">
          Sent by BoothIQ Civic Intelligence Platform. Contact your local booth officer for queries.
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""

# ── SMS text builder ──────────────────────────────────────────────────────────
def _sms_text(voter, title, body, priority):
    prefix = f"[{priority.upper()}] " if priority in ("High","Urgent") else ""
    short  = body[:100]+"..." if len(body)>100 else body
    return f"BoothIQ\n{prefix}{title}\n{short}\nBooth:{voter['booth_id']} ID:{voter['voter_id']}"

# ── send one email ────────────────────────────────────────────────────────────
def send_email(voter, title, body, notif_type, priority, link=""):
    to = voter.get("email","")
    if not to:
        return {"success":False,"voter_id":voter["voter_id"],"email":"","error":"No email on file"}
    try:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = f"[BoothIQ] {title}"
        msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
        msg["To"]      = to
        plain = f"Dear {voter['name']},\n\n{body}\n\nBooth: {voter['booth_id']} | ID: {voter['voter_id']}\n— BoothIQ"
        msg.attach(MIMEText(plain,"plain"))
        msg.attach(MIMEText(_html_email(voter,title,body,notif_type,priority,link),"html"))
        with smtplib.SMTP(SMTP_HOST,SMTP_PORT) as s:
            s.ehlo(); s.starttls(); s.login(SMTP_USER,SMTP_PASS)
            s.sendmail(SMTP_USER,to,msg.as_string())
        return {"success":True,"voter_id":voter["voter_id"],"email":to,"error":None}
    except smtplib.SMTPAuthenticationError:
        return {"success":False,"voter_id":voter["voter_id"],"email":to,
                "error":"SMTP auth failed. Check Gmail App Password."}
    except Exception as e:
        return {"success":False,"voter_id":voter["voter_id"],"email":to,"error":str(e)}

# ── send one SMS ──────────────────────────────────────────────────────────────
def send_sms(voter, title, body, notif_type, priority):
    phone = voter.get("phone","")
    if not phone:
        return {"success":False,"voter_id":voter["voter_id"],"phone":"","error":"No phone on file"}
    try:
        from twilio.rest import Client
        msg = Client(TWILIO_SID,TWILIO_TOKEN).messages.create(
            body=_sms_text(voter,title,body,priority), from_=TWILIO_FROM, to=phone)
        return {"success":True,"voter_id":voter["voter_id"],"phone":phone,"error":None,"sid":msg.sid}
    except ImportError:
        return {"success":False,"voter_id":voter["voter_id"],"phone":phone,
                "error":"Run: pip install twilio"}
    except Exception as e:
        return {"success":False,"voter_id":voter["voter_id"],"phone":phone,"error":str(e)}

# ── bulk send (main function) ─────────────────────────────────────────────────
def bulk_notify(voters, title, body, notif_type, priority,
                link="", via_email=True, via_sms=False):
    email_res, sms_res = [], []
    for v in voters:
        if via_email: email_res.append(send_email(v,title,body,notif_type,priority,link))
        if via_sms:   sms_res.append(send_sms(v,title,body,notif_type,priority))
    def summ(res):
        sent = sum(1 for r in res if r["success"])
        return {"sent":sent,"failed":len(res)-sent,"results":res}
    return {
        "total_voters": len(voters),
        "email": summ(email_res) if via_email else {"sent":0,"failed":0,"results":[]},
        "sms":   summ(sms_res)   if via_sms   else {"sent":0,"failed":0,"results":[]},
    }

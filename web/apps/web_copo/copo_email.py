import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import web.settings.email as email_settings
from web.apps.web_copo.models import User
from django.conf import settings

class CopoEmail:

    def __init__(self):
        self.messages = {
            "new_manifest" : "<h4>Manifest Available</h4><p>A manifest has been uploaded for approval. Please follow the link to proceed</p><h5>{} - {}</h5><p><a href='{}'>{}</a></p>".capitalize,
            "sample_rejected" : "<h4>Following Samples Rejected</h4><h5>{} - {}</h5><ul>{}</ul>"
        }


    def send(self, to, sub, content, html=False):
        msg = MIMEMultipart()
        msg['From'] = email_settings.mail_address

        msg['Subject'] = sub
        if html:
            msg.attach(MIMEText(content, 'html'))
        else:
            msg.attach(MIMEText(content, "plain"))
        self.mailserver = smtplib.SMTP(email_settings.mail_server, email_settings.mail_server_port)
        # identify ourselves to smtp gmail client
        self.mailserver.ehlo()
        # secure our email with tls encryption
        self.mailserver.starttls()
        # re-identify ourselves as an encrypted connection
        self.mailserver.ehlo()
        self.mailserver.login(email_settings.mail_username, email_settings.mail_password)
        self.mailserver.sendmail(email_settings.mail_address, to, msg.as_string())
        self.mailserver.quit()

    def notify_manifest_pending_approval(self, data, **kwargs):
        # get users in group
        if kwargs.get("project", "") in ["DTOL", "ASG"]:
            users = User.objects.filter(groups__name='dtol_sample_notifiers')
        elif kwargs.get("project", "") in ["ERGA"]:
            users = User.objects.filter(groups__name='erga_sample_notifiers')
        elif kwargs.get("project", "") in ["DTOL_ENV"]:
            users = User.objects.filter(groups__name='dtolenv_sample_notifiers')
        else:
            users = []
        email_addresses = list()
        sub = ""
        if len(users) > 0:
            for u in users:
                email_addresses.append(u.email)

            demo_notification = ""
            is_new = "New "
            if "demo" in data:
                demo_notification = "DEMO SERVER NOTIFICATION: "
            if not kwargs.get("is_new", True) :            
                is_new = "Modified "
            msg = self.messages["new_manifest"].format(kwargs["title"], demo_notification + kwargs["description"], data, data)
            sub = demo_notification + is_new + kwargs["project"] + " Manifest - " + kwargs["title"]
            self.send(to=email_addresses, sub=sub, content=msg, html=True)


    def notify_sample_rejected_after_approval(self, **kwargs):
        # get users in group
        if kwargs.get("project", "") in ["DTOL", "ASG"]:
            users = User.objects.filter(groups__name='dtol_sample_notifiers')
        elif kwargs.get("project", "") in ["ERGA"]:
            users = User.objects.filter(groups__name='erga_sample_notifiers')
        elif kwargs.get("project", "") in ["DTOL_ENV"]:
            users = User.objects.filter(groups__name='dtolenv_sample_notifiers')
        else:
            users = []
        email_addresses = list()
        sub = ""
        samples = kwargs["rejected_sample"] 
        sample_arr = [f"<li>{key} : {samples[key]}</li>" for key in samples.keys()]
        sample_str = ' '.join(sample_arr)

        if len(users) > 0:
            for u in users:
                email_addresses.append(u.email)
            
            msg = self.messages["sample_rejected"].format(kwargs.get("title"," ") , kwargs.get("description"," "), sample_str)
            sub = settings.ENVIRONMENT_TYPE + " " + kwargs.get("project"," ") + " Manifest - " + kwargs.get("title"," ")
            self.send(to=email_addresses, sub=sub, content=msg, html=True)
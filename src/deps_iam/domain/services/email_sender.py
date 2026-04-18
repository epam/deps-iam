import smtplib
import ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from deps_iam import constants
from deps_iam.domain.entities import OrganisationPk
from deps_iam.domain.interfaces.services import IEmailSender
from deps_iam.infrastructure.uow import UnitOfWork


class EmailSender(IEmailSender):
    TEMPLATE_NAME = "invitation_email_template.html"
    EMBED_IMAGES = ("deps-logo.png", "deps-hero-image.png")

    def __init__(
        self,
        login: str,
        password: str,
        host: str,
        port: int,
        from_addr: str,
        external_url: str,
        event_type: str,
        uow: UnitOfWork,
        user_guide_link: Optional[str] = None,
        vpn_disclaimer: Optional[str] = None,
        static_data_dir: Path = constants.PATH_TO_STATIC_DATA,
    ) -> None:
        self._login = login
        self._password = password
        self._host = host
        self._port = port
        self._from_addr = from_addr
        self._external_url = external_url
        self._user_guide_link = user_guide_link
        self._event_type = event_type
        self._vpn_disclaimer = vpn_disclaimer
        self._uow = uow
        self._ssl_context = ssl.create_default_context()
        self._static_data_dir = static_data_dir
        self._jinja_env = Environment(loader=FileSystemLoader(static_data_dir), autoescape=True)

    def send_email(self, email: str, inviter: str, organisation_pk: str) -> None:
        smtp = smtplib.SMTP(host=self._host, port=self._port)
        try:
            smtp.starttls(context=self._ssl_context)
            smtp.login(self._login, self._password)
            smtp.sendmail(self._from_addr, [email], self._build_message(email, inviter, organisation_pk))
        finally:
            smtp.quit()

    def _build_message(self, email: str, inviter: str, organisation: str) -> str:
        msg = MIMEMultipart("related")
        msg["From"] = self._from_addr
        msg["To"] = email
        msg["Sender"] = self._login
        msg["Subject"] = constants.EMAIL_INVITATION_SUBJECT
        msg[constants.EMAIL_EVENT_TYPE_HEADER] = self._event_type
        msg.attach(MIMEText(self._get_email_body(inviter, organisation), "html"))
        return self._attach_images(msg).as_string()

    def _attach_images(self, msg: MIMEMultipart) -> MIMEMultipart:
        for img in self.EMBED_IMAGES:
            path = self._static_data_dir / img
            mime_img = MIMEImage(path.read_bytes(), path.suffix[1:])
            mime_img.add_header("Content-ID", f"<{img}>")
            mime_img.add_header("Content-Disposition", "attachment", filename=img)
            msg.attach(mime_img)
        return msg

    def _get_email_body(self, inviter: str, organisation_pk: str) -> str:
        invitation_link = self._generate_invitation_link(organisation_pk)
        template = self._jinja_env.get_template(self.TEMPLATE_NAME)
        with self._uow:
            organisation = self._uow.organisation.get(OrganisationPk(organisation_pk))
        return template.render(
            inviter=inviter,
            organisation=organisation.name,
            invitation_link=invitation_link,
            support_email=self._from_addr,
            logo_cid=self.EMBED_IMAGES[0],
            hero_image_cid=self.EMBED_IMAGES[1],
            user_guide_link=self._user_guide_link,
            vpn_disclaimer=self._vpn_disclaimer,
        )

    def _generate_invitation_link(self, organisation_pk: str) -> str:
        return f"{self._external_url}/join/{organisation_pk}"

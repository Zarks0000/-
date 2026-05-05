import os
import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid, parseaddr
from typing import Optional

from flask_compat import APIRouter, Header
from pydantic import BaseModel, Field

from account import get_current_user_id

router = APIRouter()

FEEDBACK_TO_EMAIL = "madingyinan@outlook.com"


class FeedbackRequest(BaseModel):
    content: str = Field(..., min_length=1)
    contact: Optional[str] = ""
    page: Optional[str] = ""


def _env_bool(name: str, default: bool = False) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _smtp_error_text(exc: smtplib.SMTPException) -> str:
    raw = getattr(exc, "smtp_error", b"")
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="ignore")
    return str(raw or exc)


def _friendly_smtp_error(exc: Exception) -> str:
    if isinstance(exc, smtplib.SMTPAuthenticationError):
        detail = _smtp_error_text(exc).lower()
        if "5.7.139" in detail or "basic authentication is disabled" in detail:
            return (
                "SMTP 登录失败：当前 Outlook/Microsoft 邮箱已禁用账号密码式 SMTP 认证。"
                "请改用支持 SMTP 授权码/应用专用密码的发信邮箱，或为 Microsoft 邮箱接入 OAuth2/Graph 发信。"
            )
        return "SMTP 登录失败：请检查 SMTP_USER、SMTP_PASSWORD、SMTP_FROM 是否正确，并确认邮箱已开启 SMTP 服务。"
    if isinstance(exc, smtplib.SMTPConnectError):
        return "SMTP 服务器连接失败：请检查 SMTP_HOST、SMTP_PORT 和网络连接。"
    if isinstance(exc, smtplib.SMTPException):
        return f"SMTP 发送失败：{_smtp_error_text(exc) or str(exc)}"
    return str(exc)


def _as_email_address(value: Optional[str]) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    _, address = parseaddr(raw)
    if "@" not in address:
        return ""
    local, domain = address.rsplit("@", 1)
    if not local or "." not in domain:
        return ""
    return address


def _send_feedback_email(payload: FeedbackRequest, user_id: Optional[str]) -> None:
    smtp_host = (os.getenv("SMTP_HOST") or "").strip()
    smtp_port = int((os.getenv("SMTP_PORT") or "587").strip())
    smtp_user = (os.getenv("SMTP_USER") or "").strip()
    smtp_password = (os.getenv("SMTP_PASSWORD") or "").strip()
    smtp_from = (os.getenv("SMTP_FROM") or smtp_user).strip()
    use_tls = _env_bool("SMTP_USE_TLS", True)

    if not smtp_host or not smtp_from:
        raise ValueError("后端未配置 SMTP_HOST / SMTP_FROM，无法发送反馈邮件")

    message = EmailMessage()
    message["Subject"] = "摩旅客用户反馈"
    message["From"] = smtp_from
    message["To"] = FEEDBACK_TO_EMAIL
    if _env_bool("FEEDBACK_BCC_TO_SENDER", True) and smtp_from.lower() != FEEDBACK_TO_EMAIL.lower():
        message["Bcc"] = smtp_from
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain=smtp_from.split("@")[-1] if "@" in smtp_from else None)
    reply_to = _as_email_address(payload.contact)
    if reply_to:
        message["Reply-To"] = reply_to

    body = "\n".join(
        [
            "摩旅客收到一条用户反馈：",
            "",
            f"用户标识：{user_id or '未知'}",
            f"页面来源：{(payload.page or '').strip() or '未提供'}",
            f"联系方式：{(payload.contact or '').strip() or '未提供'}",
            "",
            "反馈内容：",
            payload.content.strip(),
        ]
    )
    message.set_content(body, subtype="plain", charset="utf-8")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as smtp:
        if use_tls:
            smtp.starttls()
        if smtp_user and smtp_password:
            smtp.login(smtp_user, smtp_password)
        refused = smtp.send_message(message)
        if refused:
            raise smtplib.SMTPRecipientsRefused(refused)


@router.post("/api/v1/feedback")
def submit_feedback(
    payload: FeedbackRequest,
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
):
    content = payload.content.strip()
    if not content:
        return {"status": "error", "message": "请先填写反馈内容"}

    user_id = get_current_user_id(authorization, x_user_id)
    try:
        _send_feedback_email(
            FeedbackRequest(
                content=content,
                contact=(payload.contact or "").strip(),
                page=(payload.page or "").strip(),
            ),
            user_id,
        )
    except Exception as exc:
        return {"status": "error", "message": _friendly_smtp_error(exc)}

    return {
        "status": "success",
        "message": f"反馈已发送至 {FEEDBACK_TO_EMAIL}",
    }

from config.celery import app

from apps.chambers.notifications import WelcomeChamberAdminEmailNotification

from .models import User


@app.task
def send_welcome_chamber_admin_email(chamber_admin_id: int):
    """Send welcome email to new chamber admin."""
    chamber_admin = User.objects.filter(pk=chamber_admin_id).first()
    if not chamber_admin:
        return
    WelcomeChamberAdminEmailNotification(chamber_admin=chamber_admin).send()

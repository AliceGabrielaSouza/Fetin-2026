from datetime import timedelta
from django.utils import timezone
from comunication.models import Read

def delete_old_reads():
    # Obtém a data atual
    now = timezone.now()
    # Calcula a data que está 3 dias atrás
    three_days_ago = now - timedelta(days=3)

    # Remove leituras que têm um timestamp mais antigo que três dias
    Read.objects.filter(timestamp__lt=three_days_ago).delete()
from datetime import datetime

take_year = int(datetime.now().strftime("%Y"))


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': take_year
    }

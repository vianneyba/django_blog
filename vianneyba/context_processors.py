from django.conf import settings

CATEGORIES = [
    ('jeux-video', 'Jeux Vidéo')
]

def admin_media(request):
    return {
        'WITH_COMMENT': settings.WITH_COMMENT,
        'WITH_REGISTRATION': settings.WITH_REGISTRATION,
        'TITLE_SITE': settings.TITLE_SITE,
        'CATEGORIES': CATEGORIES,
        'DEFAULT_LANG': 'French',
        'URL_IMAGE': settings.URL_IMAGE,
        'PATH_IMAGE': 'http://vianneyba.fr/images/cover',
    }
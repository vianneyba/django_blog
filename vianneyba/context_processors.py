from django.conf import settings

def admin_media(request):
    return {
        'WITH_COMMENT': settings.WITH_COMMENT,
        'WITH_REGISTRATION': settings.WITH_REGISTRATION,
    }
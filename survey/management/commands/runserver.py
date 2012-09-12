import socket

try:
    from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
except:
    print "django.contrib.staticfiles app not included in installed apps"
    print "Using django runserver instead"
    from django.core.management.commands.runserver import Command as RunserverCommand

from survey import settings

class Command(RunserverCommand):    
    def run(self, *args, **options):
        if self.addr == '127.0.0.1':
            settings.HOST_NAME = 'localhost'
        elif self.addr == '0.0.0.0':
            settings.HOST_NAME = socket.gethostname()
        settings.PORT = self.port
        if settings.PORT == '80':
            settings.HOST_URL = '{hostname}'.format(hostname=settings.HOST_NAME)
        else:
            settings.HOST_URL = '{hostname}:{port}'.format(hostname=settings.HOST_NAME, port=settings.PORT) 
        super(Command, self).run(*args, **options)
        
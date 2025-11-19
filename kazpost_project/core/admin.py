# core/admin.py
from django.contrib import admin
from .models import Department, Service, OperatorWindow, QueueTicket, ServiceTransaction

admin.site.register(Department)
admin.site.register(Service)
admin.site.register(OperatorWindow)


# "ЭТАП-2"

admin.site.register(QueueTicket)

# "ЭТАП-3"

admin.site.register(ServiceTransaction)
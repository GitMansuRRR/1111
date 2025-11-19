from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=5, unique=True) # "A", "B", etc.

    def __str__(self):
        return self.name

class OperatorWindow(models.Model):
    window_number = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    # Свяжем с оператором позже
    # current_operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.department.name} - {self.window_number}"


# ЭТАП-2

# core/models.py (добавляем в конец)

class QueueTicket(models.Model):
    # Статусы талона
    STATUS_CHOICES = [
        ('waiting', 'В ожидании'),
        ('called', 'Вызван'),
        ('done', 'Обслужен'),
    ]

    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="Услуга")
    ticket_number = models.CharField(max_length=10, verbose_name="Номер талона") # A-101
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    
    # Кто вызвал этот талон?
    called_by_window = models.ForeignKey(OperatorWindow, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Вызван окном")

    class Meta:
        verbose_name = "Талон очереди"
        verbose_name_plural = "Талоны очереди"

    def __str__(self):
        return self.ticket_number


# ЭТАП-3
class ServiceTransaction(models.Model):
    # Связываем операцию с конкретным талоном
    ticket = models.OneToOneField(QueueTicket, on_delete=models.CASCADE, verbose_name="Талон")
    
    # Детали операции
    description = models.TextField(verbose_name="Описание операции (вес, адрес и т.д.)", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость услуги", default=0)
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Время завершения")

    class Meta:
        verbose_name = "Операция обслуживания"
        verbose_name_plural = "Операции обслуживания"

    def __str__(self):
        return f"Операция по талону {self.ticket.ticket_number}"
from rest_framework import serializers
from .models import Service, QueueTicket, OperatorWindow, ServiceTransaction

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']

class OperatorWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatorWindow
        fields = ['id', 'window_number']

class QueueTicketSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    called_by_window = OperatorWindowSerializer(read_only=True)

    class Meta:
        model = QueueTicket
        fields = ['id', 'ticket_number', 'service', 'status', 'called_by_window']

# ЭТАП-3
class ServiceTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTransaction
        fields = ['ticket', 'description', 'price', 'completed_at']
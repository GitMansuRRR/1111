from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Service, QueueTicket, OperatorWindow, ServiceTransaction
from .serializers import ServiceSerializer, QueueTicketSerializer, ServiceTransactionSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class QueueTicketViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = QueueTicket.objects.all()
    serializer_class = QueueTicketSerializer

    @action(detail=False, methods=['post'])
    def create_ticket(self, request):
        service_id = request.data.get('service_id')
        if not service_id:
            return Response({'error': 'service_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

        last_ticket = QueueTicket.objects.filter(service=service).order_by('-created_at').first()
        if last_ticket:
            num = int(last_ticket.ticket_number.split('-')[1]) + 1
        else:
            num = 101

        new_ticket_number = f"{service.prefix}-{num}"

        ticket = QueueTicket.objects.create(service=service, ticket_number=new_ticket_number)
        serializer = QueueTicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['post'])
    def call_next(self, request):
        window_id = request.data.get('window_id')
        
        if not window_id:
            return Response({'error': 'window_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            window = OperatorWindow.objects.get(id=window_id)
        except OperatorWindow.DoesNotExist:
            return Response({'error': 'Window not found'}, status=status.HTTP_404_NOT_FOUND)

        # === ИСПРАВЛЕНИЕ: ЗАКРЫВАЕМ ПРЕДЫДУЩИЕ ТАЛОНЫ ===
        # Ищем все талоны, которые ЭТО окно вызывало ранее и которые еще "висят" (status='called')
        previous_tickets = QueueTicket.objects.filter(called_by_window=window, status='called')
        for old_ticket in previous_tickets:
            old_ticket.status = 'done' # Меняем статус на "Обслужен"
            old_ticket.save()
        # ================================================

        # Дальше логика такая же, как была
        next_ticket = QueueTicket.objects.filter(status='waiting').order_by('created_at').first()
        
        if not next_ticket:
            return Response({'message': 'Нет талонов в очереди'}, status=status.HTTP_404_NOT_FOUND)

        next_ticket.status = 'called'
        next_ticket.called_by_window = window
        next_ticket.save()
        
        serializer = QueueTicketSerializer(next_ticket)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_dashboard(self, request):
        tickets = QueueTicket.objects.exclude(status='done').order_by('-created_at')[:10]
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    # ЭТАП-3
    @action(detail=False, methods=['post'])
    def complete_service(self, request):
        # Получаем данные от оператора
        window_id = request.data.get('window_id')
        price = request.data.get('price', 0)
        description = request.data.get('description', '')

        if not window_id:
            return Response({'error': 'window_id required'}, status=status.HTTP_400_BAD_REQUEST)

        # Находим активный талон этого окна
        try:
            window = OperatorWindow.objects.get(id=window_id)
            # Ищем талон, который сейчас "called" (вызван) у этого окна
            current_ticket = QueueTicket.objects.get(called_by_window=window, status='called')
        except (OperatorWindow.DoesNotExist, QueueTicket.DoesNotExist):
            return Response({'error': 'Нет активного клиента для завершения'}, status=status.HTTP_404_NOT_FOUND)

        # 1. Сохраняем транзакцию (результат работы)
        transaction = ServiceTransaction.objects.create(
            ticket=current_ticket,
            price=price,
            description=description
        )

        # 2. Закрываем талон
        current_ticket.status = 'done'
        current_ticket.save()

        return Response({'message': 'Обслуживание завершено', 'ticket': current_ticket.ticket_number})


# core/views.py (добавь в конец)
from django.shortcuts import render

def terminal_view(request):
    # Эта view просто показывает HTML-файл
    return render(request, 'terminal.html')

def operator_view(request):
    # Мы "прокинем" в шаблон список окон, чтобы оператор мог себя выбрать
    windows = OperatorWindow.objects.all()
    return render(request, 'operator.html', {'windows': windows})

def dashboard_view(request):
    return render(request, 'dashboard.html')

# ЭТАП-3
def service_desk_view(request):
    windows = OperatorWindow.objects.all()
    return render(request, 'service_desk.html', {'windows': windows})

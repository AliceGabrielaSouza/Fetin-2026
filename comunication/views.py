import json

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Read, CarAssignment
from .serializers import ReadSerializer
from rest_framework.views import APIView

from django.http import JsonResponse
from datetime import datetime, timedelta

@api_view(['POST'])
def Make_Read(request):

    serializer = ReadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': 'Dados invalidos.', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    car = serializer.validated_data.get('car')

    if car is None:
        return Response({'error': 'O carro é obrigatório.'},status=400
        )

    now = timezone.now()

    assignment = CarAssignment.objects.filter(car=car,start_date__lte=now.date(),end_date__gte=now.date()).select_related('user').first()
    if assignment is None:
        return Response({
                'error': 'Não existe funcionário atribuído a este carro neste período.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    read = serializer.save(client=assignment.user)
    delete_old_reads()

    return Response(
        {
            'message': 'Dados salvos com sucesso!',
            'client': assignment.user.username,
            'car': car.identifier,
            'read_id': read.pk,
        },
        status=status.HTTP_201_CREATED
    )


def delete_old_reads():

    threshold_date = timezone.now() - timedelta(days=3)
    Read.objects.filter(timestamp__lt=threshold_date).delete()

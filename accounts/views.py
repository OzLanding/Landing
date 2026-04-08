from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Account
from .serializers import AccountSerializer


class AccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = Account.objects.filter(user=request.user, is_active=True)
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Account, pk=pk, user=user, is_active=True)

    def get(self, request, pk):
        account = self.get_object(pk, request.user)
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    def delete(self, request, pk):
        account = self.get_object(pk, request.user)
        account.is_active = False
        account.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
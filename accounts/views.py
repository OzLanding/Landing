from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import AccountSerializer
from .services import AccountService


class AccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = AccountService.get_accounts(request.user)
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AccountService.create_account(serializer, request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccountDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        account = AccountService.get_account(pk, request.user)
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    def delete(self, request, pk):
        account = AccountService.get_account(pk, request.user)
        AccountService.delete_account(account)
        return Response(status=status.HTTP_204_NO_CONTENT)
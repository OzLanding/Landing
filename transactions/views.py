from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from transactions.repositories import TransactionRepository
from transactions.serializers import TransactionDetailSerializer, TransactionSerializer
from transactions.services import TransactionService


class TransactionListCreateView(ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = TransactionRepository.get_user_transactions(self.request.user)

        filters = {
            "transaction_type": self.request.query_params.get("transaction_type"),
            "category": self.request.query_params.get("category"),
            "min_amount": self.request.query_params.get("min_amount"),
            "max_amount": self.request.query_params.get("max_amount"),
            "start_date": self.request.query_params.get("start_date"),
            "end_date": self.request.query_params.get("end_date"),
        }

        return TransactionRepository.apply_filters(queryset, filters)

    def perform_create(self, serializer):
        TransactionService.create_transaction(self.request.user, serializer)


class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TransactionRepository.get_user_transactions(self.request.user)

    def perform_update(self, serializer):
        TransactionService.update_transaction(serializer.instance, serializer)

    def perform_destroy(self, instance):
        TransactionService.delete_transaction(instance)

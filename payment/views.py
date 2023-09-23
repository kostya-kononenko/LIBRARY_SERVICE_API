from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Payment

from payment.permissions import IsAdminOrIfAuthenticatedReadOnly
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all().select_related("user", "borrowing")
    serializer_class = PaymentSerializer
    permission_classes = [
        IsAdminOrIfAuthenticatedReadOnly,
    ]

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action == "list":
            serializer_class = PaymentListSerializer
        elif self.action == "retrieve":
            serializer_class = PaymentDetailSerializer

        return serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SuccessPaymentView(APIView):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id")
        print(session_id)
        payment = Payment.objects.filter(session_id=session_id).first()
        if payment:
            payment.status = "PAID"
            payment.save()

            return Response(
                {"message": "Borrowing payed successfully"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Payment not found or already processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CancelPaymentView(APIView):
    def get(self, request, *args, **kwargs):
        borrowing_id = kwargs.get("pk")
        payment = Payment.objects.filter(
            borrowing_id=borrowing_id).first()

        if payment:
            return Response(
                {"message": "Payment can be paid a bit later"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Payment not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q

from clients.models import Client
from projects.models import Project, Task
from invoices.models import Invoice


class AnalyticsDashboardView(APIView):

    def get(self, request):

        total_clients = Client.objects.count()
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status="ACTIVE").count()

        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status="DONE").count()

        total_revenue = Invoice.objects.filter(status="PAID").aggregate(
            total=Sum("total")
        )["total"] or 0

        pending_revenue = Invoice.objects.exclude(status="PAID").aggregate(
            total=Sum("total")
        )["total"] or 0

        return Response({
            "total_clients": total_clients,
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "total_revenue": total_revenue,
            "pending_revenue": pending_revenue,
        })
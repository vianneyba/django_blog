# requests_box/views.py
from django.conf import settings
from django.contrib import messages
from django.core.mail import mail_admins
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import SiteRequestForm

class RequestCreateView(View):
    template_name = "requests_box/form.html"

    def get(self, request):
        form = SiteRequestForm(user=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SiteRequestForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        obj = form.save(commit=False)
        if request.user.is_authenticated:
            obj.user = request.user
        obj.save()

        # mail_admins(
        #     subject=f"[Demande] {obj.get_kind_display()}",
        #     message=(
        #         f"De : {obj.name} <{obj.email}>\n"
        #         f"Identifiant : {obj.username or '-'}\n"
        #         f"Type : {obj.get_kind_display()}\n\n"
        #         f"{obj.message}\n"
        #     ),
        # )
        messages.success(request, "Ta demande a bien été envoyée.")
        return redirect(reverse("requests_box:create"))
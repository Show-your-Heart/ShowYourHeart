import yaml
from django.shortcuts import get_object_or_404, redirect, render

from apps.demo.forms import DataForm
from apps.demo.models import Data


def create_view(request):
    if request.method == "GET":
        form = DataForm()
    else:
        form = DataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("list")
    return render(request, "create.html", {"form": form})


def list_view(request):
    context = {"data": Data.objects.all()}
    return render(request, "list.html", context)


def detail_view(request, id):
    obj = get_object_or_404(Data, pk=id)
    obj.field_select_checkbox = yaml.safe_load(obj.field_select_checkbox)
    obj.save()
    form = DataForm(instance=obj)
    for field in form.fields:
        form.fields.get(field).disabled = True
    return render(request, "details.html", {"form": form})


def update_view(request, id):
    obj = get_object_or_404(Data, pk=id)
    if request.method == "GET":
        obj.field_select_checkbox = yaml.safe_load(obj.field_select_checkbox)
        obj.save()
        form = DataForm(instance=obj)
        return render(request, "update.html", {"form": form})
    else:
        form = DataForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
        return redirect("details", obj.id)

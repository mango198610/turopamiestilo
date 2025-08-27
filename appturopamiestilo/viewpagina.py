
from datetime import datetime

from django.shortcuts import render

from appturopamiestilo.models import Producto


def paginainicio(request):
    data = {'title': 'Pagina Web'}
    data['fecha'] = datetime.now()
    data['producto'] = Producto.objects.all()
    return render(request ,"index.html" ,  data)
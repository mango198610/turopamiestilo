
from datetime import datetime

from django.shortcuts import render


def paginainicio(request):
    data = {'title': 'Pagina Web'}
    data['fecha'] = datetime.now()
    return render(request ,"index.html" ,  data)
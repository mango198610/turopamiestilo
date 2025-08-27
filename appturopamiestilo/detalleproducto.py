from django.shortcuts import render

from appturopamiestilo.models import AccesoModulo, Producto, StockProducto
from appturopamiestilo.views import addUserData


def view(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']


        else:
            data = {'title':'Datelle Producto'}
            addUserData(request, data)
            producto=Producto.objects.get(id=int(request.GET['id']))
            stockpoducto=StockProducto.objects.filter(producto=producto)
            data['dataproducto']=producto
            data['listastockproducto']=stockpoducto
            data['logo']='logo-2.png'

            return render(request, "paginaweb/detalle_producto.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)
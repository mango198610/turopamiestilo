import json

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str as force_text
from appturopamiestilo.funciones import ip_client_address
from appturopamiestilo.models import AccesoModulo, StockProducto, Producto, TipoSize
from appturopamiestilo.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')

def view(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']

            if action == 'agregar':
                try:
                    data = {'title': ''}
                    if int(request.POST.get('id')) == 0:

                        mensaje = 'Nueva stock'
                        client_address = ip_client_address(request)
                        producto=Producto.objects.get(id=int(request.POST.get('idproducto')))

                        listdatositems = json.loads(request.POST['listadatositems'])
                        for d in listdatositems:
                            stock = StockProducto(producto=producto,tipo_id=int(request.POST.get('cmbtamano')),
                                                  color=d['color'],precio=d['precio'],stock=d['cantidad'])
                            stock.save()


                            LogEntry.objects.log_action(
                                user_id=request.user.pk,
                                content_type_id=ContentType.objects.get_for_model(stock).pk,
                                object_id=stock.id,
                                object_repr=force_text(stock),
                                action_flag=ADDITION if int(request.POST['id']) == 0 else CHANGE,
                                change_message=mensaje + ' (' + client_address + ')')


                    else:
                        mensaje = 'Actualizado stock'



                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as ex:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(ex)}),
                                        content_type="application/json")


            elif action == 'serverSide':
                try:
                    lista = []
                    filtrado = False
                    draw = int(request.POST.get('draw', 1))
                    start = int(request.POST.get('start', 0))
                    length = int(request.POST.get('length', 10))

                    accesomodulo = AccesoModulo.objects.get(id=int(request.POST['permisopcion[acc]']))

                    listastock = StockProducto.objects.filter(producto_id=int(request.POST['idproducto']))
                    registros_total = listastock.count()

                    if request.POST['columns[0][search][value]'] != '':
                        tamano = int(request.POST['columns[0][search][value]'])
                        listastock = listastock.filter(tipo_id=tamano)
                        filtrado = True


                    listastock = listastock.order_by('tipo__nombre')
                    registros = listastock[start:start + length] if length != -1 else listastock
                    registros_filtrado = listastock.count()

                    for d in registros:
                        htmlAcciones = ''

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="eliminarStock(' + str(
                            d.id) + ',\'' + str(
                            d.tipo.nombre).upper() + '\');"><i class="dw dw-delete-3"></i>  Eliminar</a></li>'

                        if d.estado:
                            htmlestado = '<span class="badge bg-success fs-6">ACTIVO</span>'
                        else:
                            htmlestado = '<span class="badge bg-danger fs-6">INACTIVO</span>'


                        lista.append({
                            'tamano': str(d.tipo.nombre).upper(),
                            'color': '<span class="btn"  style="background: '+ d.color +' ;color: white;cursor: context-menu" data-bgcolor="#FA1D06" data-color="#ffffff" ></span>',
                            'precio': str(d.precio),
                            'cantidadexistente': str(d.stock),
                            'cantidadminima': str(d.stockminimo),
                            'estado': htmlestado,
                              'acciones': f'''
                                        <div class="dropdown">
                                            <button class="btn btn-primary dropdown-toggle" type="button" id="dropdownMenu2" data-bs-toggle="dropdown" aria-expanded="false">
                                                Acciones
                                            </button>
                                            <ul class="dropdown-menu" aria-labelledby="dropdownMenu2">
                                                {htmlAcciones}
                                            </ul>
                                        </div>
                                    '''
                        })

                    estado = [{"id": 1, "nombre": "ACTIVO"},
                                     {"id": 2, "nombre": "INACTIVO"}]

                    tipotamano = [{"id": x.id, "nombre": x.nombre} for x in TipoSize.objects.filter(estado=True)]

                    respuesta = {
                        'draw': draw,
                        'recordsTotal': registros_total,
                        'recordsFiltered': registros_filtrado,
                        'data': lista,
                        'filtro-select-estado': list(estado),
                        'filtro-select-tamano': list(tipotamano),
                        'placeholderBusqueda': 'Buscar el nombre ',
                        'result': 'ok',
                        'filtrado': filtrado
                    }

                    return HttpResponse(json.dumps(respuesta), content_type="application/json")
                except Exception as e:
                    print(e)
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")

            elif action == 'eliminar':
                try:
                    stock=StockProducto.objects.get(pk=int(request.POST['id']))
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(stock).pk,
                        object_id=stock.id,
                        object_repr=force_text(stock),
                        action_flag=DELETION,
                        change_message=str('stock eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    stock.delete()

                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")

        else:
            data = {'title':'Stock'}
            addUserData(request, data)
            if 'action' in request.GET:
                action = request.GET['action']

            else:
                data['permisopcion'] = AccesoModulo.objects.get(id=int(request.GET['acc']))
                producto = Producto.objects.get(pk=request.GET['id'])
                data['producto'] = producto
                data['listatamano'] = TipoSize.objects.filter(estado=True)

                return render(request, "mantenimiento/stock.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)
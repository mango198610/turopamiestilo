import json
from datetime import datetime
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str as force_text
from appturopamiestilo.funciones import ip_client_address
from appturopamiestilo.models import AccesoModulo, Categoria, Producto
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
                        if Producto.objects.filter(nombre=str(request.POST.get('txtnombre')).upper().strip()).exists():
                            return HttpResponse(
                                json.dumps({'result': 'bad', 'message': 'El proudcto ya se encuentra registrada'}),
                                content_type="application/json")
                        mensaje = 'Nueva producto'

                        producto = Producto(nombre=str(request.POST.get('txtnombre')).upper().strip(),
                                          categoria_id=int(request.POST.get('cmbcategoria')),
                                          descripcion=str(request.POST.get('txtdescripcion')).upper(),
                                          fecha_registro=datetime.now())


                    else:
                        mensaje = 'Actualizado producto'

                    producto.save()

                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(producto).pk,
                        object_id=producto.id,
                        object_repr=force_text(producto),
                        action_flag=ADDITION if int(request.POST['id']) == 0 else CHANGE,
                        change_message=mensaje + ' (' + client_address + ')')
                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as ex:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(ex)}),
                                        content_type="application/json")

            if action == 'serverSide':
                try:
                    lista = []
                    filtrado = False
                    draw = int(request.POST.get('draw', 1))
                    start = int(request.POST.get('start', 0))
                    length = int(request.POST.get('length', 10))

                    listaproducto = Producto.objects.filter()
                    registros_total = listaproducto.count()


                    if request.POST['columns[2][search][value]'] != '':
                        search = request.POST['columns[2][search][value]']
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listaproducto = listaproducto.filter(
                                    nombre__icontains=search).order_by('nombre')
                                filtrado = True
                            else:
                                listaproducto = listaproducto.filter(
                                    Q(nombre__icontains=ss[0]) & Q(
                                        nombre__icontains=ss[1])).order_by('nombre')
                                filtrado = True




                    listaproducto = listaproducto.order_by('nombre')
                    registros = listaproducto[start:start + length] if length != -1 else listaproducto
                    registros_filtrado = listaproducto.count()

                    for d in registros:
                        htmlAcciones = ''

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="editar(' + str(
                            d.id) + ');"><i class="dw dw-edit-2"></i>  Editar</a></li>'

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="eliminarProducto(' + str(
                            d.id) + ',\'' + str(
                            d.nombre).upper() + '\');"><i class="dw dw-delete-3"></i>  Eliminar</a></li>'
                        if d.estado:
                            htmlestado = '<span class="badge bg-success fs-6">ACTIVO</span>'
                        else:
                            htmlestado = '<span class="badge bg-danger fs-6">INACTIVO</span>'


                        lista.append({
                            'nombre': str(d.nombre),
                            'categoria': str(d.categoria.nombre).upper(),
                            'descripcion': str(d.descripcion).upper(),
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
                    categoria =[{"id": x.id, "nombre": x.nombre} for x in Categoria.objects.filter(estado=True)]


                    respuesta = {
                        'draw': draw,
                        'recordsTotal': registros_total,
                        'recordsFiltered': registros_filtrado,
                        'data': lista,
                        'filtro-select-categoria': list(categoria),
                        'filtro-select-estado': list(estado),
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
                    producto=Producto.objects.get(pk=int(request.POST['id']))
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(producto).pk,
                        object_id=producto.id,
                        object_repr=force_text(producto),
                        action_flag=DELETION,
                        change_message=str('producto eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    producto.delete()

                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")

        else:
            data = {'title':'Productos'}
            addUserData(request, data)
            data['permisopcion'] = AccesoModulo.objects.get(id=int(request.GET['acc']))
            data['listacategoria'] = Categoria.objects.filter(estado=True)


            return render(request, "mantenimiento/producto.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)
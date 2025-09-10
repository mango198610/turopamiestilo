import json

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str as force_text
from appturopamiestilo.funciones import ip_client_address
from appturopamiestilo.models import AccesoModulo, StockProducto, Producto, TipoSize, ImagenProducto
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

                        mensaje = 'Nueva Imagen'
                        client_address = ip_client_address(request)
                        producto=Producto.objects.get(id=int(request.POST.get('idproducto')))

                        imagendata = ImagenProducto(nombre=str(request.POST['txtnombre']).upper(),producto=producto,orden=int(request.POST.get('cmborden')),
                                                    color=str(request.POST.get('txtcolor')))


                    else:
                        mensaje = 'Actualizado Imagen'

                    # preguntar si viene una imagen del producto
                    if "imglogo" in request.FILES:
                        imagendata.imagen = request.FILES["imglogo"]

                    imagendata.save()

                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(imagendata).pk,
                        object_id=imagendata.id,
                        object_repr=force_text(imagendata),
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

                    accesomodulo = AccesoModulo.objects.get(id=int(request.POST['permisopcion[acc]']))

                    listaimagen = ImagenProducto.objects.filter(producto_id=int(request.POST['idproducto']))
                    registros_total = listaimagen.count()



                    listaimagen = listaimagen.order_by('nombre')
                    registros = listaimagen[start:start + length] if length != -1 else listaimagen
                    registros_filtrado = listaimagen.count()

                    for d in registros:
                        htmlAcciones = ''

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="eliminarImagen(' + str(
                            d.id) + ',\'' + str(
                            d.nombre).upper() + '\');"><i class="dw dw-delete-3"></i>  Eliminar</a></li>'

                        if d.estado:
                            htmlestado = '<span class="badge bg-success fs-6">ACTIVO</span>'
                        else:
                            htmlestado = '<span class="badge bg-danger fs-6">INACTIVO</span>'

                        if d.imagen:
                            htmimagen = '<img class="bg-soft-primary rounded img-fluid avatar-40 me-3" src="../turopamiestilo/media' + d.imagen.url + '" alt="logo">'
                        else:
                            htmimagen = '<img class="bg-soft-primary rounded img-fluid avatar-40 me-3" src="../turopamiestilo/static/assets/images/shapes/01.png" alt="logo">'


                        lista.append({
                            'nombre': str(d.nombre).upper(),
                            'orden': d.orden,
                            'imagen': htmimagen,
                            'color': '<span class="btn"  style="background: '+ d.color +' ;color: white;cursor: context-menu" data-bgcolor="#FA1D06" data-color="#ffffff" ></span>',
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

                    respuesta = {
                        'draw': draw,
                        'recordsTotal': registros_total,
                        'recordsFiltered': registros_filtrado,
                        'data': lista,
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
                    dataimagen=ImagenProducto.objects.get(pk=int(request.POST['id']))
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(dataimagen).pk,
                        object_id=dataimagen.id,
                        object_repr=force_text(dataimagen),
                        action_flag=DELETION,
                        change_message=str('imagen eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    dataimagen.delete()

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

                return render(request, "mantenimiento/imagenproducto.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import Solicitud, Participante
from .forms import SolicitudForm, ParticipanteForm, UsuarioForm, UsuarioEditarForm


def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='Administrador').exists()
    )


def is_staff_user(user):
    return user.is_authenticated and (
        is_admin(user) or user.groups.filter(name='Operador').exists()
    )


def home(request):
    return redirect('dashboard' if request.user.is_authenticated else 'login')


class LoginSIGCE(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos. Comprueba tus credenciales.')
        return super().form_invalid(form)


@require_POST
def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
@user_passes_test(is_staff_user)
def dashboard(request):
    context = {
        'total': Solicitud.objects.count(),
        'recibidas': Solicitud.objects.filter(estado='RECIBIDA').count(),
        'en_proceso': Solicitud.objects.filter(estado='EN_PROCESO').count(),
        'resueltas': Solicitud.objects.filter(estado='RESUELTA').count(),
        'recientes': Solicitud.objects.order_by('-id')[:5],
    }
    return render(request, 'core/dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def solicitudes(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    items = Solicitud.objects.all().order_by('-id')
    if q:
        items = items.filter(
            Q(numero__icontains=q)
            | Q(asunto__icontains=q)
            | Q(solicitante__icontains=q)
        )
    if estado:
        items = items.filter(estado=estado)
    return render(request, 'core/solicitudes.html', {'items': items, 'q': q, 'estado': estado})


@login_required
@user_passes_test(is_staff_user)
def solicitud_nueva(request):
    form = SolicitudForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save()
        messages.success(request, 'Solicitud registrada correctamente.')
        return redirect('solicitud_detalle', pk=obj.pk)
    return render(
        request,
        'core/form.html',
        {'form': form, 'heading': 'Nueva solicitud', 'lead': 'HU-01 · Registro de solicitud', 'submit': 'Guardar'},
    )


@login_required
@user_passes_test(is_staff_user)
def solicitud_detalle(request, pk):
    obj = get_object_or_404(Solicitud, pk=pk)
    participantes = obj.participantes.all() if hasattr(obj, 'participantes') else []
    return render(request, 'core/detalle.html', {'obj': obj, 'participantes': participantes})


@login_required
@user_passes_test(is_staff_user)
def solicitud_editar(request, pk):
    obj = get_object_or_404(Solicitud, pk=pk)
    form = SolicitudForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Solicitud actualizada.')
        return redirect('solicitud_detalle', pk=obj.pk)
    return render(
        request,
        'core/form.html',
        {'form': form, 'heading': 'Editar solicitud', 'lead': obj.numero, 'submit': 'Guardar cambios'},
    )


@login_required
@user_passes_test(is_staff_user)
def participante_nuevo(request, pk):
    obj = get_object_or_404(Solicitud, pk=pk)
    form = ParticipanteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        participante = form.save(commit=False)
        participante.solicitud = obj
        participante.save()
        messages.success(request, 'Participante registrado.')
        return redirect('solicitud_detalle', pk=obj.pk)
    return render(
        request,
        'core/form.html',
        {'form': form, 'heading': 'Añadir participante', 'lead': f'HU-02 · {obj.numero}', 'submit': 'Guardar'},
    )


@login_required
@user_passes_test(is_admin)
def usuarios(request):
    items = User.objects.prefetch_related('groups').order_by('username')
    return render(request, 'core/usuarios.html', {'items': items})


@login_required
@user_passes_test(is_admin)
def usuario_nuevo(request):
    form = UsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario registrado correctamente.')
        return redirect('usuarios')
    return render(
        request,
        'core/form.html',
        {'form': form, 'heading': 'Nuevo usuario', 'lead': 'HU-17 · Control de usuarios y roles', 'submit': 'Guardar'},
    )


@login_required
@user_passes_test(is_admin)
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    form = UsuarioEditarForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('usuarios')
    return render(
        request,
        'core/form.html',
        {'form': form, 'heading': 'Editar usuario', 'lead': usuario.username, 'submit': 'Guardar cambios'},
    )


@login_required
@user_passes_test(is_admin)
def usuario_clave(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    form = SetPasswordForm(usuario, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Contraseña actualizada correctamente.')
        return redirect('usuarios')
    return render(
        request,
        'core/form.html',
        {'form': form, 'heading': 'Cambiar contraseña', 'lead': usuario.username, 'submit': 'Actualizar contraseña'},
    )
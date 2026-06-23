import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Usuario

# --- PATRONES DE VALIDACIÓN ---
REGEX_DOCUMENTO = re.compile(r'^\d{5,12}$')
REGEX_NOMBRES   = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]{2,50}$')
REGEX_EMAIL     = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$')
REGEX_PASSWORD  = re.compile(r'^(?=.*[A-Z])(?=.*\d).{8,}$')

# --- HELPERS DE ROL ---
def es_administrador(user):
    return user.is_authenticated and user.rol == 'ADMINISTRADOR'

def es_aprendiz(user):
    return user.is_authenticated and user.rol == 'APRENDIZ'


# --- VISTAS DE ACCESO ---

def home(request):
    return redirect('login')


def login_user(request):
    if request.user.is_authenticated:
        if request.user.rol == 'ADMINISTRADOR':
            return redirect('admin_dashboard')
        return redirect('apprentice_dashboard')

    if request.method == 'POST':
        documento = request.POST.get('documento', '').strip()
        password  = request.POST.get('password', '')

        if not REGEX_DOCUMENTO.match(documento):
            messages.error(request, "El documento debe contener entre 5 y 12 dígitos numéricos.")
            return render(request, 'login.html')

        if len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return render(request, 'login.html')

        try:
            user_obj = Usuario.objects.get(documento=documento)
            user = authenticate(request, username=user_obj.username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido, {user.first_name or user.documento}!")
                if user.rol == 'ADMINISTRADOR':
                    return redirect('admin_dashboard')
                return redirect('apprentice_dashboard')
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Usuario.DoesNotExist:
            messages.error(request, "El documento ingresado no está registrado.")

    return render(request, 'login.html')


@require_POST
def register_user(request):
    """Solo acepta POST. Rechaza cualquier acceso GET directo a esta ruta."""
    nombres   = request.POST.get('nombres', '').strip()
    apellidos = request.POST.get('apellidos', '').strip()
    email     = request.POST.get('email', '').strip()
    documento = request.POST.get('documento', '').strip()
    rol       = request.POST.get('rol', '')
    password  = request.POST.get('password', '')

    if not REGEX_NOMBRES.match(nombres):
        messages.error(request, "Los nombres solo deben contener letras y espacios (2–50 caracteres).")
        return redirect('login')

    if not REGEX_NOMBRES.match(apellidos):
        messages.error(request, "Los apellidos solo deben contener letras y espacios (2–50 caracteres).")
        return redirect('login')

    if not REGEX_EMAIL.match(email):
        messages.error(request, "El correo electrónico no tiene un formato válido.")
        return redirect('login')

    if not REGEX_DOCUMENTO.match(documento):
        messages.error(request, "El documento debe contener entre 5 y 12 dígitos numéricos.")
        return redirect('login')

    if not REGEX_PASSWORD.match(password):
        messages.error(request, "La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número.")
        return redirect('login')

    # Validación estricta del rol (evita manipulación del formulario)
    if rol not in ('ADMINISTRADOR', 'APRENDIZ'):
        messages.error(request, "El rol seleccionado no es válido.")
        return redirect('login')

    if Usuario.objects.filter(documento=documento).exists():
        messages.error(request, "Ya existe un usuario con ese número de documento.")
        return redirect('login')

    if Usuario.objects.filter(email=email).exists():
        messages.error(request, "Ya existe una cuenta registrada con ese correo electrónico.")
        return redirect('login')

    Usuario.objects.create_user(
        username=documento,
        password=password,
        first_name=nombres,
        last_name=apellidos,
        email=email,
        documento=documento,
        rol=rol,
    )
    messages.success(request, "Cuenta creada exitosamente. Ahora puedes iniciar sesión.")
    return redirect('login')


def logout_user(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('login')


# --- DASHBOARDS ---

@login_required(login_url='login')
@user_passes_test(es_administrador, login_url='login')
def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.rol != 'ADMINISTRADOR':
        messages.error(request, "Acceso denegado. Se requiere rol de Administrador.")
        return redirect('login')

    users = Usuario.objects.all().order_by('date_joined')
    query = request.GET.get('q', '').strip()
    if query:
        users = users.filter(first_name__icontains=query) | users.filter(documento__icontains=query)

    paginator = Paginator(users, 5)  # 5 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard.html', {
        'users': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


@login_required(login_url='login')
@user_passes_test(es_aprendiz, login_url='login')
def apprentice_dashboard(request):
    return render(request, 'apprentice_dashboard.html')


# --- CRUD ---

@login_required(login_url='login')
@user_passes_test(es_administrador, login_url='login')
@require_POST
def user_delete(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('admin_dashboard')

    user = get_object_or_404(Usuario, id=user_id)
    user.delete()
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect('admin_dashboard')


@login_required(login_url='login')
@user_passes_test(es_administrador, login_url='login')
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        nombres      = request.POST.get('nombres', '').strip()
        apellidos    = request.POST.get('apellidos', '').strip()
        email        = request.POST.get('email', '').strip()
        documento    = request.POST.get('documento', '').strip()
        rol          = request.POST.get('rol', '')
        new_password = request.POST.get('password', '')

        errores = {}

        if not REGEX_NOMBRES.match(nombres):
            errores['nombres'] = "Solo letras y espacios (2–50 caracteres)."
        if not REGEX_NOMBRES.match(apellidos):
            errores['apellidos'] = "Solo letras y espacios (2–50 caracteres)."
        if not REGEX_EMAIL.match(email):
            errores['email'] = "Formato de correo no válido."
        if not REGEX_DOCUMENTO.match(documento):
            errores['documento'] = "Entre 5 y 12 dígitos numéricos."
        if new_password and not REGEX_PASSWORD.match(new_password):
            errores['password'] = "Mínimo 8 caracteres, una mayúscula y un número."
        if rol not in ('ADMINISTRADOR', 'APRENDIZ'):
            errores['rol'] = "Rol no válido."
        if Usuario.objects.filter(documento=documento).exclude(id=user_id).exists():
            errores['documento'] = "Ese documento ya está en uso por otro usuario."
        if Usuario.objects.filter(email=email).exclude(id=user_id).exists():
            errores['email'] = "Ese correo ya está en uso por otro usuario."

        if errores:
            for msg in errores.values():
                messages.error(request, msg)
            return render(request, 'edit_user.html', {'user_to_edit': user_to_edit})

        user_to_edit.first_name = nombres
        user_to_edit.last_name  = apellidos
        user_to_edit.email      = email
        user_to_edit.documento  = documento
        user_to_edit.rol        = rol

        if new_password:
            user_to_edit.set_password(new_password)

        user_to_edit.save()
        messages.success(request, f"Datos de {user_to_edit.first_name} actualizados correctamente.")
        return redirect('admin_dashboard')

    return render(request, 'edit_user.html', {'user_to_edit': user_to_edit})

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)
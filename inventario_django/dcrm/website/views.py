from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Usuario

def home(request):
    return redirect('login')

def login_user(request):
    if request.user.is_authenticated:
        if request.user.rol == 'ADMINISTRADOR':
            return redirect('admin_dashboard')
        else:
            return redirect('apprentice_dashboard')

    if request.method == 'POST':
        documento = request.POST.get('documento')
        password = request.POST.get('password')
        try:
            user_obj = Usuario.objects.get(documento=documento)
            username = user_obj.username
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido {user.get_rol_display()}!")
                if user.rol == 'ADMINISTRADOR':
                    return redirect('admin_dashboard')
                else:
                    return redirect('apprentice_dashboard')
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Usuario.DoesNotExist:
            messages.error(request, "El documento ingresado no está registrado.")
    
    return render(request, 'login.html')

def register_user(request):
    if request.method == 'POST':
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        documento = request.POST.get('documento')
        rol = request.POST.get('rol')
        password = request.POST.get('password')

        if Usuario.objects.filter(documento=documento).exists():
            messages.error(request, "Ya existe un usuario con este documento.")
            return redirect('login')
        
        nuevo_usuario = Usuario.objects.create_user(
            username=documento,
            password=password,
            first_name=nombres,
            last_name=apellidos,
            email=email,
            documento=documento,
            rol=rol
        )
        nuevo_usuario.save()
        messages.success(request, "Cuenta creada exitosamente. Ahora puedes iniciar sesión.")
        return redirect('login')
    return redirect('login')

def logout_user(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('login')

def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.rol != 'ADMINISTRADOR':
        messages.error(request, "Acceso denegado. Se requiere rol de Administrador.")
        return redirect('login')
    
    users = Usuario.objects.all()

    query = request.GET.get('q', '')
    if query:
        users = users.filter(first_name__icontains=query) | users.filter(documento__icontains=query)
        
    return render(request, 'admin_dashboard.html', {'users': users})

def apprentice_dashboard(request):
    if not request.user.is_authenticated or request.user.rol != 'APRENDIZ':
        messages.error(request, "Acceso denegado. Se requiere rol de Aprendiz.")
        return redirect('login')
    
    return render(request, 'apprentice_dashboard.html')

def user_delete(request, user_id):
    if not request.user.is_authenticated or request.user.rol != 'ADMINISTRADOR':
        return redirect('login')
    user = Usuario.objects.get(id=user_id)
    user.delete()
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect('admin_dashboard')

def edit_user(request, user_id):
    if not request.user.is_authenticated or request.user.rol != 'ADMINISTRADOR':
        return redirect('login')
    
    user_to_edit = Usuario.objects.get(id=user_id)
    
    if request.method == 'POST':
        user_to_edit.first_name = request.POST.get('nombres')
        user_to_edit.last_name = request.POST.get('apellidos')
        user_to_edit.email = request.POST.get('email')
        user_to_edit.documento = request.POST.get('documento')
        user_to_edit.rol = request.POST.get('rol')
        
        new_password = request.POST.get('password')
        if new_password:
            user_to_edit.set_password(new_password)
            
        user_to_edit.save()
        messages.success(request, f"Datos de {user_to_edit.first_name} actualizados.")
        return redirect('admin_dashboard')
        
    return render(request, 'edit_user.html', {'user_to_edit': user_to_edit})

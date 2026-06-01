import os
from django import forms
from django.conf import settings
from app.usuarios.models import Usuario
from app.estudiante.models import Estudiante
from app.docente.models import Docente
from app.academico.models import Carrera, Paralelo, Semestre, AsignacionDocente, Materia, Horario

from app.reconocimientoFacial.face_services import generar_encoding
import os
from django.conf import settings

# Formulario de estudiante y edición de estudiante
class EstudianteCreacionForm(forms.ModelForm):
    # Campos para crear el usuario
    username = forms.CharField(label='RU', max_length=10)
    first_name = forms.CharField(label='Nombres', max_length=100)
    last_name = forms.CharField(label='Apellidos', max_length=100)
    telefono = forms.CharField(label='Telefono', max_length= 8)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)   # sin max_length
    confirm_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)  # sin max_length
    # Campos del modelo Estudiante
    paralelo = forms.ModelChoiceField(queryset=Paralelo.objects.all(), required=True)
    semestre = forms.ModelChoiceField(queryset=Semestre.objects.all(), required=True)
    foto = forms.ImageField(required=False, label='Foto del rostro')  # Usamos ImageField para la subida


    class Meta:
        model = Estudiante
        fields = ['fecha_nacimiento', 'correo_institucional']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded p-2'}),
            'correo_institucional': forms.EmailInput(attrs={'class': 'w-full border-b-2 border-gray-300 focus:border-gray-500 outline-none px-2 py-2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-2 py-2'
            })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(codUsuario=username).exists():
            raise forms.ValidationError('Ya existe un usuario con este RU')
        return username
    
    def clean_correo_institucional(self):
        correo = self.cleaned_data.get('correo_institucional')
        if Estudiante.objects.filter(correo_institucional=correo).exists():
            raise forms.ValidationError('Ya existe un usuario con este Email')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Las contraseñas no son iguales')
        return cleaned_data

    def save(self, commit=True):
        username = self.cleaned_data['username']
        correo = self.cleaned_data.get('correo_institucional')
        password = self.cleaned_data['password']
        
        # Crear usuario en tabla usuarios_usuario
        user = Usuario(
            codUsuario=username,
            password=password,
        )
        user.save()

        # Procesar la foto si se subió
        foto_upload = self.cleaned_data.get('foto')
        foto_path = ''
        if foto_upload:
            # Definir ruta de guardado: media/rostros/RU_nombre
            extension = os.path.splitext(foto_upload.name)[1]
            nombre_archivo = f"{username}_{self.cleaned_data['first_name']}{extension}"
            ruta_relativa = os.path.join('rostros', nombre_archivo)
            ruta_completa = os.path.join(settings.MEDIA_ROOT, ruta_relativa)
            # Guardar el archivo
            with open(ruta_completa, 'wb+') as destino:
                for chunk in foto_upload.chunks():
                    destino.write(chunk)
            foto_path = ruta_relativa

        # Crear estudiante
        estudiante = super().save(commit=False)
        estudiante.RU = int(username) 
        estudiante.usuario = user
        estudiante.nombre = self.cleaned_data['first_name']
        estudiante.apellido = self.cleaned_data['last_name']

        estudiante.telefono = self.cleaned_data['telefono']
        estudiante.carrera = Carrera.objects.first()
        estudiante.paralelo= self.cleaned_data['paralelo']
        estudiante.semestre = self.cleaned_data['semestre']
        estudiante.foto = foto_path  
        
        #Generar encoding facial si se subió una foto
        if foto_path:
            encoding = generar_encoding(foto_path)
            if encoding:
                estudiante.encoding = encoding

        estudiante.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        
        if commit:
            estudiante.save()
        return estudiante


class EstudianteEdicionForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombres', max_length=100)
    last_name = forms.CharField(label='Apellidos', max_length=100)
    telefono = forms.CharField(label='Numero de telefono', max_length=8)
    password = forms.CharField(label='Nueva contraseña (opcional)', required=False, widget=forms.PasswordInput)
    nueva_foto = forms.ImageField(label='Cambiar foto (opcional)', required=False)

    class Meta:
        model = Estudiante
        fields = ['fecha_nacimiento', 'correo_institucional', 'paralelo', 'semestre']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded p-2'}),
            'correo_institucional': forms.EmailInput(attrs={'class': 'w-full border rounded p-2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-2 py-2'
            })
    
        if self.instance and self.instance.usuario:
            self.fields['first_name'].initial = self.instance.nombre
            self.fields['last_name'].initial = self.instance.apellido
            self.fields['correo_institucional'].initial = self.instance.correo_institucional
            self.fields['telefono'].initial = self.instance.telefono
       
       
 
    def save(self, commit=True):
        estudiante = super().save(commit=False)
        usuario = estudiante.usuario
        
        # Actualizar contraseña si se proporcionó una nueva
        password = self.cleaned_data.get('password')
        if password:
            usuario.password = password
            usuario.save()
        
        # Actualizar campos del estudiante
        estudiante.nombre = self.cleaned_data['first_name']
        estudiante.apellido = self.cleaned_data['last_name']
        estudiante.correo_institucional = self.cleaned_data['correo_institucional']
        estudiante.telefono = self.cleaned_data['telefono']
        
        # Procesar nueva foto si se subió
        nueva_foto = self.cleaned_data.get('nueva_foto')

        if nueva_foto:
            username = usuario.codUsuario
            extension = os.path.splitext(nueva_foto.name)[1]
            nombre_archivo = f"{username}_{self.cleaned_data['first_name']}{extension}"
            ruta_relativa = os.path.join('rostros', nombre_archivo)
            ruta_completa = os.path.join(settings.MEDIA_ROOT, ruta_relativa)

            with open(ruta_completa, 'wb+') as destino:
                for chunk in nueva_foto.chunks():
                    destino.write(chunk)

            estudiante.foto = ruta_relativa

            #Generar nuevo encoding facial
            encoding = generar_encoding(ruta_relativa)

            if encoding:
                estudiante.encoding = encoding
        #guardar datos
        if commit:
            estudiante.save()
        return estudiante


# Formulario para creación y edición de docentes

class DocenteCreacionForm(forms.ModelForm):
    username = forms.CharField(label='Código de docente', max_length=10)
    first_name = forms.CharField(label='Nombres', max_length=100)
    last_name = forms.CharField(label='Apellidos', max_length=100)
    telefono = forms.IntegerField(label='Telefono')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    materia = forms.ModelChoiceField(queryset=Materia.objects.all(), required=True, widget=forms.Select(attrs={'class': 'w-full border rounded p-2'}))
    
    paralelo = forms.ModelChoiceField(queryset=Paralelo.objects.all(), required=True, widget=forms.Select(attrs={'class': 'w-full border rounded p-2'}))
    
    horario = forms.ModelChoiceField(queryset=Horario.objects.all(), required=True, widget=forms.Select(attrs={'class': 'w-full border rounded p-2'}) )


    class Meta:
        model = Docente
        fields = ['fecha_nacimiento', 'correo_institucional']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded p-2'}),
            'correo_institucional': forms.EmailInput(attrs={'class': 'w-full border-b-2 border-gray-300 focus:border-gray-500 outline-none px-2 py-2'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-2 py-2'
            })

        if 'paralelo' in self.data:
            try:
                paralelo_id = int(self.data.get('paralelo'))
                paralelo = Paralelo.objects.get(pk=paralelo_id)
                self.fields['semestre'].initial = paralelo.semestre
            except:
                pass
        


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(codUsuario=username).exists():
            raise forms.ValidationError('Ya existe un usuario con este codigo')
        return username
    
    def clean_correo_institucional(self):
        correo = self.cleaned_data.get('correo_institucional')
        if Docente.objects.filter(correo_institucional=correo).exists():
            raise forms.ValidationError('Ya existe un usuario con este Email')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned_data

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        correo = self.cleaned_data.get('correo_institucional')
        user = Usuario(
            codUsuario=username,
            password=password,
        )
        user.save()

        docente = super().save(commit=False)
        docente.codDocente = int(username)   # asegura que sea entero
        docente.usuario = user

        docente.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        docente.telefono = self.cleaned_data['telefono']
        
        docente.nombre = self.cleaned_data['first_name']
        docente.apellido = self.cleaned_data['last_name']
        docente.carrera = Carrera.objects.first()
        
        if commit:
            docente.save()

            #CREAR ASIGNACIÓN
            AsignacionDocente.objects.create(
                docente=docente,
                materia=self.cleaned_data['materia'],
                paralelo=self.cleaned_data['paralelo'],
                horario=self.cleaned_data['horario']
            )

        return docente


class DocenteEdicionForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombres', max_length=100)
    last_name = forms.CharField(label='Apellidos', max_length=100)
    telefono = forms.CharField(label='Telefono', max_length=8)
    password = forms.CharField(label='Nueva contraseña (opcional)', required=False, widget=forms.PasswordInput)


    materia = forms.ModelChoiceField(
        queryset=Materia.objects.all(),
        required=True
    )


    paralelo = forms.ModelChoiceField(
        queryset=Paralelo.objects.all(),
        required=True
    )

    horario = forms.ModelChoiceField(
        queryset=Horario.objects.all(),
        required=True
    )    

    class Meta:
        model = Docente
        fields = ['fecha_nacimiento', 'correo_institucional']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded p-2'}),
            'correo_institucional': forms.EmailInput(attrs={'class': 'w-full border rounded p-2'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 px-2 py-2'
            })
        
        if self.instance:
            self.fields['first_name'].initial = self.instance.nombre
            self.fields['last_name'].initial = self.instance.apellido
            self.fields['telefono'].initial = self.instance.telefono
            self.fields['correo_institucional'].initial = self.instance.correo_institucional
            
        asignacion = AsignacionDocente.objects.filter(docente=self.instance).first()

        if asignacion:
            self.fields['materia'].initial = asignacion.materia
            self.fields['paralelo'].initial = asignacion.paralelo
            self.fields['horario'].initial = asignacion.horario  




    def save(self, commit=True):
        docente = super().save(commit=False)
        usuario = docente.usuario
        password = self.cleaned_data.get('password')
        
        if password:
            usuario.password = password
            usuario.save()
        docente.nombre = self.cleaned_data['first_name']
        docente.apellido = self.cleaned_data['last_name']

        docente.correo_institucional = self.cleaned_data['correo_institucional']
        docente.telefono = self.cleaned_data['telefono']


        if commit:
            docente.save()

            asignacion = AsignacionDocente.objects.filter(docente=docente).first()

            if asignacion:
                asignacion.materia = self.cleaned_data['materia']
                asignacion.paralelo = self.cleaned_data['paralelo']
                asignacion.horario = self.cleaned_data['horario']
                asignacion.save()
            else:
                AsignacionDocente.objects.create(
                    docente=docente,
                    materia=self.cleaned_data['materia'],
                    paralelo=self.cleaned_data['paralelo'],
                    horario=self.cleaned_data['horario']
                )
        return docente
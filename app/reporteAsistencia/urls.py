from django.urls import path
from . import views

app_name = "reporteAsistencia"

urlpatterns = [

    path("direccion/diario/", views.reporte_direccionCarrera_diario, name="reporteDiario_direccionCarrera"),
    path("direccion/diario/pdf/", views.exportar_direccionCarrera_diario_pdf, name="pdf_diario_direccionCarrera"),
    path("direccion/global/", views.reporte_direccionCarrera_global, name="reporteGlobal_direccionCarrera"),
    path("direccion/global/pdf/", views.exportar_direccionCarrera_global_pdf, name="pdf_global_direccionCarrera"),        
    
    path("estudiante/<int:ru>/", views.reporte_estudiante, name="reporte_estudiante"),
    path("estudiante/pdf/<int:ru>/", views.exportar_estudiante_pdf, name="pdf_reporteEstudiante"),
    
    path("docente/<int:codDocente>/diario/", views.reporte_docente_diario, name="reporteDiario_docente"),
    path("docente/diario/pdf/<int:codDocente>/", views.exportar_docente_diario_pdf, name="pdf_diario_docente"),
    path("docente/global/<int:codDocente>/", views.reporte_docente_global, name="reporteGlobal_docente"),
    path("docente/global/pdf/<int:codDocente>/", views.exportar_docente_global_pdf, name="pdf_global_docente"),


]
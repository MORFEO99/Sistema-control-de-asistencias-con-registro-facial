from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'inline; filename="Reporte de asistencia.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error al generar PDF", status=400)

    return response
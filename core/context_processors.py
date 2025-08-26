from .models import ConfiguracaoEmpresa

def empresa_context(request):
    """
    Context processor para disponibilizar configurações da empresa
    em todos os templates
    """
    try:
        empresa = ConfiguracaoEmpresa.get_instance()
        return {
            'empresa': empresa
        }
    except Exception:
        return {
            'empresa': None
        }
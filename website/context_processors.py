from . models import SiteConfiguration


def site_config(request):
    try:
        site_config_obj = SiteConfiguration.objects.first()
    except Exception as e:
        site_config_obj = None
    return {'site_config': site_config_obj}

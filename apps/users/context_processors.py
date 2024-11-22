def current_url_name(request):
    return {"current_url_name": request.resolver_match.url_name}

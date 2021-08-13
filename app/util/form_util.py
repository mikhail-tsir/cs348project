def validate_form(request, form_fields):
    for field in form_fields:
        if not request.form.get(field):
            return False
    
    return True

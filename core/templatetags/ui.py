from django import template

register = template.Library()


@register.filter
def bs(field):
    widget = field.field.widget
    name = widget.__class__.__name__
    if name in ("Select", "SelectMultiple"):
        css = "form-select"
    elif name == "CheckboxInput":
        css = "form-check-input"
    else:
        css = "form-control"
    if field.errors:
        css += " is-invalid"
    existing = widget.attrs.get("class", "")
    return field.as_widget(attrs={"class": f"{existing} {css}".strip()})


@register.filter
def is_wide(field):
    return field.field.widget.__class__.__name__ == "Textarea" or field.name in ("site_address", "subject")

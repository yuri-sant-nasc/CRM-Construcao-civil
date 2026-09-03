import csv

from django.http import HttpResponse


def export_csv(model_name, queryset, fieldnames):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    for item in queryset:
        row = {}
        for field in fieldnames:
            value = getattr(item, field)
            if callable(value):
                value = value()
            # Prevent CSV Injection (Formula Injection)
            if isinstance(value, str) and value.startswith(('=', '+', '-', '@', '\t', '\r')):
                value = f"'{value}"
            row[field] = value
        writer.writerow(row)
    return response

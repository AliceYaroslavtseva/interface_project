from django.core.paginator import Paginator


def paginator_for_page(posts, request, LIMIT):
    paginator = Paginator(posts, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

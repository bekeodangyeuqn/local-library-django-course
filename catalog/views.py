import datetime
from typing import Any
from catalog.models import Book, Author, BookInstance, Genre

from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from catalog.forms import RenewBookModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
# Create your views here.


def index(request):
    """View function for home page of site"""
    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()

    # Available books (status = 'a)
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_authors': num_authors,
        'num_instances_available': num_instances_available,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)

    return render(request, 'catalog/book_detail.html', context={'book': book})


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        context['books'] = context['author'].book_set.all()
        return context


def author_detail_view(request, primary_key):
    author = get_object_or_404(Author, pk=primary_key)
    return render(request, 'catalog/auhtor_detail.html', context={'author': author})


class LoanedBooksByUserListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    permission_required = "catalog.can_mark_returned"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("-due_back")
        )


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian"""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # if this is a POST request then process the form data
    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        # Check if form is valid
        if form.is_valid():
            # process the data in form.cleaned_data as required
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            return HttpResponseRedirect(reverse('manage-books'))

    # if this is a GET (or anthoer method) create the default form
    else:
        propsed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(
            initial={'due_back': propsed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class LoanedBooksManageListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    permission_required = "catalog.view_list_on_loan"
    template_name = "catalog/bookinstance_list_manage.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.all()
            .filter(status__exact="o")
            .order_by("-due_back")
            .select_related("borrower")
        )


class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name',
              'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name',
              'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

from http.client import BAD_REQUEST
from urllib.request import Request
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import *
from django.http import request
from datetime import datetime, timedelta
from django.contrib import messages
from django.views import View
import logging
import boto3
import os
from botocore.exceptions import ClientError
from .snsContent import Publisher

a_publisher = Publisher()
class UserAccessMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return redirect('library:home')
        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)




class UserLoginView(LoginView):
    template_name='library/login.html'
    fields='__all__'
    redirect_authenticated_user=True

    def get_success_url(self):
        return reverse_lazy('library:home')
        
def registerUser(request):
    page = 'register'
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = True
            user.save()
            messages.success(request, 'Succefully Registered!')
            return redirect('library:home')
        else:
            messages.error(request, "An error occured while registering user!")

    context={
        'page':page,
        'form':form
    }
    return render(request, 'library/register.html', context)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name='library/main.html'
    

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['accounts']=Account.objects.all()
        context['books'] = Book.objects.all()
        search_input=self.request.GET.get('search-area') or ''
        if search_input:
            context['books']=context['books'].filter(
                title__startswith=search_input)

        context['search_input']=search_input
        return context


class BookView(LoginRequiredMixin, ListView):
    model=Book
    context_object_name='books'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['books']=context['books']

        search_input=self.request.GET.get('search-area') or ''
        if search_input:
            context['books']=context['books'].filter(
                title__startswith=search_input)

        context['search_input']=search_input

        return context

class BookDetail(LoginRequiredMixin, DetailView):
    model=Book
    context_object_name='book'
    template_name='library/book.html'


class StudentView(LoginRequiredMixin, UserAccessMixin, ListView):
    model=Account
    context_object_name='students'
    permission_required = 'students.view_students'
    template_name='library/student_list.html'

    def get_context_data(self,  *args,**kwargs):
        context=super().get_context_data(**kwargs)
        context['students']=Account.objects.all()
        context['students']=context['students'].exclude(is_admin=True)
        search_input=self.request.GET.get('search-area') or ''
        if search_input:
            context['students']=context['students'].filter(name__startswith=search_input)

        context['search_input']=search_input

        return context

class StudentDetail(LoginRequiredMixin, DetailView):
    model=Account
    context_object_name='student'
    template_name='library/student.html'


class BorrowerView(LoginRequiredMixin, ListView):
    model=Borrower
    context_object_name='borrowers'
    template_name = 'library/borrower_list.html'


    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        if self.request.user.is_admin or self.request.user.is_superuser:
            context['borrowers']=context['borrowers']
        else:
            context['borrowers']=context['borrowers'].filter(student = self.request.user.id)
        return context


class BorrowerDetail(LoginRequiredMixin,  DetailView):
    model=Borrower()
    context_object_name='borrower'
    template_name='library/borrower.html'


class registerStudent(View):
    def get(self,request,id="0"):
        if id=="0":
            form = RegistrationForm()
            context={
            'form':form
            }
            return render(request, 'library/register.html', context)
        else:
            student = Account.objects.get(pk=id)
            form = AccountUpdateForm(instance = student)
            context={
            'form':form
            }
            return render(request, 'library/student_update.html', context)

    def post(self, request, id="0"):
        if id=="0":
            form = RegistrationForm(request.POST, request.FILES)
        else:
            student = Account.objects.get(pk=id)
            form = AccountUpdateForm(request.POST,request.FILES,instance=student)  
        if form.is_valid():
            form.save()
            imgName = request.FILES['pic'].name;
            upload_file("lmsstudents",os.path.join("media/students", imgName))
            messages.success(request, 'Succefully Registered!')
            return redirect('library:student-list')
        else:
            messages.error(request, "An error occured while registering Student!")


class deleteStudent(LoginRequiredMixin):
    def delete(request, id="0"):
        student = Account.objects.get(pk = id)
        student.delete()
        return redirect('library:student-list')


class deleteBook(LoginRequiredMixin):
    def delete(request, id = "0"):
        book = Book.objects.get(pk = id)
        book.delete()
        return redirect('library:book-list')
        

class borrowerDelete(LoginRequiredMixin):
    def delete(requesr, id = "0"):
        borrower = Borrower.objects.get(pk = id)
        borrower.delete()
        return redirect('library:borrower-list')

# class bookCreate(LoginRequiredMixin, UserAccessMixin, CreateView):
#     model=Book
#     permission_required= 'books.add_books'
#     fields='__all__'
#     success_url=reverse_lazy('library:book-list')


#     def form_valid(self, form):
#         form.instance.user=self.request.user
#         return super(bookCreate, self).form_valid(form)
class bookCreate(LoginRequiredMixin,View):
    def get(self,request,id="0"):
        if id=="0":
            form = BookForm()
            context={
            'form':form
            }
            return render(request, 'library/book_form.html', context)
        else:
            book = Book.objects.get(pk=id)
            form = BookForm(instance = book)
            context={
            'form':form
            }
            return render(request, 'library/book_form.html', context)

    def post(self, request, id="0"):
        if id=="0":
            form = BookForm(request.POST,request.FILES)
            
        else:
            book = Book.objects.get(pk=id)
            form = BookForm(request.POST,request.FILES,instance=book)
            
        
        if form.is_valid():
            form.save()
            imgName = request.FILES['pic'].name;
            # upload_file("lmsbooks",imgName)
            upload_file("lmsbooks",os.path.join("media/books", imgName))
            messages.success(request, 'Succefully added a new book!')
            return redirect('library:book-list')
        else:
            messages.error(request, "An error occured while adding a book!")
    
def upload_file(bucket,file_name, object_key=None):
        """Upload a file to an S3 bucket
        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param key: S3 object key. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        if object_key is None:
            object_key = file_name
        
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, bucket, object_key)
            '''
            # an example of using the ExtraArgs optional parameter to set the ACL (access control list) value 'public-read' to the S3 object
            response = s3_client.upload_file(file_name, bucket, key, 
            ExtraArgs={'ACL': 'public-read'})
            '''
        except ClientError as e:
            logging.error(e)
            return False
        return True    
            
   


class borrowBook(LoginRequiredMixin,View):

    def get(self,request,id="0"):
        if id=="0":
            form = IssueBook()
            context={
            'form':form
            }
            return render(request, 'library/borrower_form.html', context)
        else:
            book = Borrower.objects.get(pk=id)
            form = IssueBook(instance = book)
            context={
            'form':form
            }
            return render(request, 'library/borrower_form.html', context)
        

    def post(self, request, id="0"):
        result="0";
        if id=="0":
            form = IssueBook(request.POST)
        else:
            book = Borrower.objects.get(pk=id)
            form = IssueBook(request.POST,instance=book)  
        if form.is_valid():
            instance = form.save(commit=False)
            book = Book.objects.get(id=instance.book.id)
            # string = "You have issued "+book
            student = Account.objects.get(id=instance.student.id)
            if len(student.borrowed)<6:
                result=reduceCpy(student, book,instance)
                print(result)
                if result=="1":
                    messages.error(self.request, "Book not in stock")
                if result == "2":
                    messages.error(self.request,"Book is already borrowed by the student.")                   
            else:
                    messages.error(self.request,"Student has reached the maximum book count.")
            form.save()
            a_publisher.send_SMS_message("+353899543363", "Issued a book")
            if result=="0":
                messages.success(request, 'Succefully issued a book!')
            return redirect('library:borrower-list')
        else:
            messages.error(request, "An error occured while issuing a book to Student!")


def reduceCpy(student,book,instance):
    if student.id not in book.borrowers:
        if book.available_copies > 0:
            book.available_copies -= 1
            book.timesIssued+=1
            book.save()
            instance.save()
            return "0"
        else:
            return "1"
    else:
         return "2"


class createChart(View):
    def projectOnChart(request):
        labels=[]
        data=[]

        querySet = Book.objects.order_by('-timesIssued')[:5]
        for books in querySet:
            labels.append(books.title)
            data.append(books.timesIssued)
        return render(request,'library/charts.html', {
            'labels':labels,
            'data':data
        })














  
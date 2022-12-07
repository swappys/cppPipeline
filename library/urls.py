from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView



app_name = 'library'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    


    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='library:login'), name='logout'),
    path('register/', registerStudent.as_view(), name='register'),


    path('books/', BookView.as_view(), name='book-list'),
    path('book/create/', bookCreate.as_view(), name='book-create'),
    path('book/<slug:pk>/', BookDetail.as_view(), name= 'book'),
    path('book/<slug:id>/update/',bookCreate.as_view(), name='book-update'),
    path('book/<slug:id>/delete/', deleteBook.delete, name='book-delete'),
    path('book/charts', createChart.projectOnChart, name='show-chart'),


    path('students/', StudentView.as_view(), name='student-list'),
    path('student/create/', registerStudent.as_view(), name='student-create'),
    path('student/<slug:pk>/', StudentDetail.as_view(), name='student-detail'),
    path('student/<slug:id>/update/', registerStudent.as_view(), name='student-update'),
    path('student/<slug:id>/delete/', deleteStudent.delete, name='student-delete'),



    path('borrowers/', BorrowerView.as_view(), name='borrower-list'),
    path('borrower/create/', borrowBook.as_view(), name='borrower-create'),
    path('borrower/<slug:pk>/', BorrowerDetail.as_view(), name= 'borrower'),
    path('borrower/<slug:id>/update/', borrowBook.as_view(), name='borrower-update'),
    path('borrower/<slug:id>/delete/', borrowerDelete.delete, name='borrower-delete'),





]

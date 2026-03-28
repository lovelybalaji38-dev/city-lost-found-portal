from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-item/<str:item_status>/', views.add_item, name='add_item'),
    path('items/<str:item_status>/', views.list_items, name='list_items'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('item/<int:pk>/edit/', views.edit_item, name='edit_item'),
    path('item/<int:pk>/delete/', views.delete_item, name='delete_item'),
    path('item/<int:pk>/claim/', views.claim_item, name='claim_item'),
    path('claim/<int:claim_id>/approve/', views.approve_claim, name='approve_claim'),
    path('chat/<int:item_id>/', views.chat_view, name='chat'),
    path('claim/<int:claim_id>/decline/', views.decline_claim, name='decline_claim'),
    path('delete-claim/<int:claim_id>/', views.delete_claim, name='delete_claim'),
    path('users/', views.users_overview, name='users_overview')
]
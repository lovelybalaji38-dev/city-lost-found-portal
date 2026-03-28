from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Item
from .forms import ItemForm
from django.views.decorators.cache import never_cache
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Claim
from django.contrib.auth.decorators import login_required
from .models import Chat
from django.contrib.auth.models import User
from django.db.models import Count, Q

from .models import Claim, ClaimImage





def home(request):
    # Recent items
    recent_items = Item.objects.all().order_by('-id')[:8]

    # Stats
    lost_count = Item.objects.filter(status='lost').count()
    found_count = Item.objects.filter(status='found').count()
    total_items = Item.objects.count()

    # 🔥 ADD THIS BLOCK
    approved_items = []

    if request.user.is_authenticated:
        approved_items = Claim.objects.filter(
            claimant=request.user,
            status='approved'
        ).values_list('item_id', flat=True)

    return render(request, 'home.html', {
        'recent_items': recent_items,
        'lost_count': lost_count,
        'found_count': found_count,
        'total_items': total_items,
        'approved_items': approved_items,   # 🔥 IMPORTANT
    })




@login_required
@never_cache


def dashboard(request):

    # Existing logic
    if request.user.is_superuser:
        user_items = Item.objects.all()
        claims = Claim.objects.all()
    else:
        user_items = Item.objects.filter(user=request.user)
        claims = Claim.objects.filter(item__user=request.user)

    # 🔥 ADD THIS (Admin stats)
    total_users = User.objects.count()

    users_data = User.objects.annotate(
        total_posts=Count('items'),
        lost_count=Count('items', filter=Q(items__status='lost')),
        found_count=Count('items', filter=Q(items__status='found')),
    )

    context = {
        'user_items': user_items,
        'claims': claims,

        # 👇 NEW DATA
        'total_users': total_users,
        'users_data': users_data,
    }

    return render(request, 'dashboard.html', context)


    
 



@login_required
@never_cache
def add_item(request, item_status):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.status = item_status
            item.user = request.user   # 🔥 IMPORTANT
            item.save()

            messages.success(request, f"{item_status.capitalize()} item added successfully!")
            return redirect('dashboard')
    else:
        form = ItemForm(initial={'status': item_status})

    template_name = 'add_lost_item.html' if item_status == 'lost' else 'add_found_item.html'
    return render(request, template_name, {'form': form, 'status': item_status})


def list_items(request, item_status):
    query = request.GET.get('q')

    items = Item.objects.filter(status=item_status).order_by('-id')

    if query:
        items = items.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        )

    template_name = 'lost_items.html' if item_status == 'lost' else 'found_items.html'

    return render(request, template_name, {
    'items': items,
    'query': query,
    'item_status': item_status
})


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'item_detail.html', {'item': item})


@login_required
@never_cache
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)


    # 🔥 ADMIN + OWNER மட்டும்
    if not (request.user.is_superuser or item.user == request.user):
     return HttpResponseForbidden("You are not allowed to edit this item")

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully!")
            return redirect('dashboard')
    else:
        form = ItemForm(instance=item)

    return render(request, 'edit_item.html', {'form': form, 'item': item})


@login_required
@never_cache
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)

    # 🔐 ADMIN + OWNER CHECK
    if not (request.user.is_superuser or item.user == request.user):
       return HttpResponseForbidden("You are not allowed to delete this item")

    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('dashboard')

    return render(request, 'delete_item.html', {'item': item})




@login_required
def claim_item(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        message = request.POST.get('message')

        # 🔥 FIRST: claim create pannunga
        claim = Claim.objects.create(
            item=item,
            claimant=request.user,
            message=message
        )

        # 🔥 THEN: images save pannunga
        files = request.FILES.getlist('images')

        for f in files:
            ClaimImage.objects.create(claim=claim, image=f)

        messages.success(request, "Claim request sent!")
        return redirect('item_detail', pk=pk)

    return render(request, 'claim_form.html', {'item': item})


@login_required
def approve_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)

    
    if claim.item.user != request.user and not request.user.is_superuser:
      return redirect('home')

    claim.status = 'approved'
    claim.save()

    messages.success(request, "Claim Approved!")

    return redirect('dashboard')



@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)

    approved = False
    has_claim = False   # 👈 ADD THIS

    if request.user.is_authenticated:

    # 🔥 already claim pannirukana check
     has_claim = Claim.objects.filter(
        item=item,
        claimant=request.user
    ).exists()

    # 🔥 approved check
    if request.user.is_superuser:
        approved = True
    else:
        approved = Claim.objects.filter(
            item=item,
            claimant=request.user,
            status='approved'
        ).exists()

    return render(request, 'item_detail.html', {
        'item': item,
        'approved': approved,
        'has_claim': has_claim   
    })




@login_required
def chat_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # 🔐 allow owner OR approved claimant OR admin
    approved = Claim.objects.filter(
        item=item,
        claimant=request.user,
        status='approved'
    ).exists()

    if not (request.user == item.user or approved or request.user.is_superuser):
        return redirect('home')

    # 📩 SEND MESSAGE
    if request.method == "POST":
        msg = request.POST.get('message')

        if msg:   # avoid empty message

            # 🔄 sender / receiver logic
            if request.user == item.user or request.user.is_superuser:
                claim = Claim.objects.filter(item=item, status='approved').first()
                if claim:
                    receiver = claim.claimant
                else:
                    return redirect('home')   # safety
            else:
                receiver = item.user

            Chat.objects.create(
                item=item,
                sender=request.user,
                receiver=receiver,
                message=msg
            )

    # 📜 GET MESSAGES
    messages = Chat.objects.filter(item=item).order_by('timestamp')

    return render(request, 'chat.html', {
        'messages': messages,
        'item': item
    })


@login_required
def decline_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)

    # owner or admin mattum
    if claim.item.user != request.user and not request.user.is_superuser:
        return redirect('home')

    claim.status = 'rejected'
    claim.save()

    messages.success(request, "Claim Rejected!")
    return redirect('dashboard')



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def delete_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)

    # only owner அல்லது admin மட்டும் delete பண்ணலாம்
    if request.user == claim.item.user or request.user.is_superuser:
        claim.delete()

    return redirect('dashboard')



from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def users_overview(request):
    users_data = User.objects.annotate(
        total_posts=Count('items'),
        lost_count=Count('items', filter=Q(items__status='lost')),
        found_count=Count('items', filter=Q(items__status='found')),
    )

    total_users = User.objects.count()

    return render(request, 'users_overview.html', {
        'users_data': users_data,
        'total_users': total_users,
    })

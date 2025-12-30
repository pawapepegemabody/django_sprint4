from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from .forms import OrderForm, ReviewForm, UserEditForm
from .models import Box, Order, Review, ServiceType

User = get_user_model()


def index(request):
    order_list = Order.objects.select_related(
        'service_type', 'box', 'client', 'washer'
    ).filter(
        is_published=True,
        service_type__is_published=True,
        appointment_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('reviews')
    ).order_by('-appointment_date')
    paginator = Paginator(order_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    order = get_object_or_404(
        Order.objects.select_related(
            'service_type', 'box', 'client', 'washer'
        ),
        id=id
    )
    if not order.client == request.user:
        if (not order.is_published or
                (order.service_type and not order.service_type.is_published) or
                order.appointment_date > timezone.now()):
            return redirect('blog:index')
    reviews = order.reviews.all()
    form = ReviewForm()
    context = {
        'post': order,
        'comments': reviews,
        'form': form
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    service_type = get_object_or_404(
        ServiceType,
        slug=category_slug,
        is_published=True
    )
    order_list = Order.objects.select_related(
        'service_type', 'box', 'client', 'washer'
    ).filter(
        service_type=service_type,
        is_published=True,
        appointment_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('reviews')
    ).order_by('-appointment_date')
    paginator = Paginator(order_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': service_type,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    form = OrderForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        order = form.save(commit=False)
        order.client = request.user
        if order.service_type:
            order.price = order.service_type.price
        order.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    order = get_object_or_404(Order, id=post_id)
    if order.client != request.user:
        return redirect('blog:post_detail', id=post_id)
    form = OrderForm(
        request.POST or None,
        files=request.FILES or None,
        instance=order
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    order = get_object_or_404(Order, id=post_id)
    if order.client != request.user:
        return redirect('blog:post_detail', id=post_id)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        order.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    order_list = Order.objects.filter(
        client=profile_user
    ).select_related(
        'service_type', 'box', 'client', 'washer'
    ).annotate(
        comment_count=Count('reviews')
    ).order_by('-appointment_date')
    paginator = Paginator(order_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile_user,
        'page_obj': page_obj
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = UserEditForm(
        request.POST or None,
        instance=request.user
    )
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def add_comment(request, post_id):
    order = get_object_or_404(Order, id=post_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        review.order = order
        review.save()
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    review = get_object_or_404(Review, id=comment_id, order_id=post_id)
    if review.author != request.user:
        return redirect('blog:post_detail', id=post_id)
    form = ReviewForm(request.POST or None, instance=review)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/comment.html', {'form': form, 'comment': review})


@login_required
def delete_comment(request, post_id, comment_id):
    review = get_object_or_404(Review, id=comment_id, order_id=post_id)
    if review.author != request.user:
        return redirect('blog:post_detail', id=post_id)
    if request.method == 'POST':
        review.delete()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/comment.html', {'comment': review})


class RegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')

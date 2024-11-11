from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from .forms import SignUpForm, LoginForm, EditProfileForm, CommentForm
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Post, Profile, User, Comment


class HomeView(ListView):
    template_name = 'core/home.html'
    queryset = Post.objects.all()
    paginate_by = 2


class PostView(DetailView):
    model = Post
    template_name = 'core/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # since our slug field is not unique, we need the primary key to get a unique post
        pk = self.kwargs['pk']
        slug = self.kwargs['slug']

        post = get_object_or_404(Post, pk=pk, slug=slug)
        context['post'] = post
        return context




def signup(request):
    """
    This function handles the signup process for new users.
    It first checks if the user is already logged in, in which case it redirects them to the home page.
    If the request method is POST,
    it processes the form data, creates a new user with the provided email and password, 
    and logs them in if the data is correct. 
    If the user is not authenticated, an error message is displayed
    """
    # If the user is already logged in, we redirect them to the home page
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # display a nice message when a new user is registered
            messages.success(request, "Congratulations, you are now a registered user!")
            return redirect('home')
    else: # return signUpForm
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})




def log_in(request):
    """
    This function handles the login process for users. It first checks if the user is already logged in,
    in which case it redirects them to the home page. If the request method is POST, it processes the
    form data, authenticates the user with their email and password, and logs them in if the data is
    correct. If the user is not authenticated, an error message is displayed.

    Parameters:
    request (HttpRequest): The request object containing the user's input data.

    Returns:
    HttpResponseRedirect or render: If the user is already logged in, it returns a redirect to the home page.
    If the request method is POST and the form is valid, it returns a redirect to the home page.
    If the request method is not POST, it returns a render of the login template with an empty form.
    """
    # If the user is already logged in, we redirect them to the home page
    if request.user.is_authenticated:
        return redirect('core:home')

    # If the request method is POST, we process the form data
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            # We check if the data is correct
            user = authenticate(email=email, password=password)
            if user:  # If the returned object is not None
                login(request, user)  # we connect the user
                return redirect('core:home')
            else:  # otherwise, an error will be displayed
                messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})





def log_out(request):
    logout(request)
    return redirect(reverse('login'))



@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'users/profile.html', {'profile': profile, 'user': user})



@login_required
def edit_profile(request):
    """
    This function handles the editing of a user's profile. It checks if the request method is POST,
    in which case it processes the form data. If the form is valid, it updates the user's profile
    information and redirects to the user's profile page. If the request method is not POST, it
    renders the edit profile template with an empty form.

    Parameters:
    request (HttpRequest): The request object containing the user's input data.

    Returns:
    HttpResponseRedirect or render: If the request method is POST and the form is valid, it returns
    a redirect to the user's profile page. If the request method is not POST, it returns a render
    of the edit profile template with an empty form.
    """
    if request.method == "POST":
        form = EditProfileForm(request.user.username, request.POST, request.FILES)
        if form.is_valid():
            about_me = form.cleaned_data["about_me"]
            username = form.cleaned_data["username"]
            image = form.cleaned_data["image"]

            user = User.objects.get(id=request.user.id)
            profile = Profile.objects.get(user=user)
            user.username = username
            user.save()
            profile.about_me = about_me
            if image:
                profile.image = image
            profile.save()
            return redirect("users:profile", username=user.username)
    else:
        form = EditProfileForm(request.user.username)
    return render(request, "users/edit_profile.html", {'form': form})




# Handles Create, Delete and Update Posts section
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "content", "image", "tags"]

    def get_success_url(self):
        messages.success(
            self.request, 'Your post has been created successfully.')
        return reverse_lazy("core:home")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.slug = slugify(form.cleaned_data['title'])
        obj.save()
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "content", "image", "tags"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        update = True
        context['update'] = update

        return context

    def get_success_url(self):
        messages.success(
            self.request, 'Your post has been updated successfully.')
        return reverse_lazy("core:home")

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post

    def get_success_url(self):
        messages.success(
            self.request, 'Your post has been deleted successfully.')
        return reverse_lazy("core:home")

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)


# Handles my users and viewers comments


class PostView(DetailView):
    model = Post
    template_name = "core/post.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs["pk"]
        slug = self.kwargs["slug"]

        form = CommentForm()
        post = get_object_or_404(Post, pk=pk, slug=slug)
        comments = post.comment_set.all()

        context['post'] = post
        context['comments'] = comments
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)

        post = Post.objects.filter(id=self.kwargs['pk'])[0]
        comments = post.comment_set.all()

        context['post'] = post
        context['comments'] = comments
        context['form'] = form

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            content = form.cleaned_data['content']

            comment = Comment.objects.create(
                name=name, email=email, content=content, post=post
            )

            form = CommentForm()
            context['form'] = form
            return self.render_to_response(context=context)

        return self.render_to_response(context=context)
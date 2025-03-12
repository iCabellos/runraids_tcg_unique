from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from core.forms import MemberLoginForm
from core.models import Member


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MemberLoginForm()
        return context

    def post(self, request):
        form = MemberLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            member = Member.objects.get(phone=phone)

            request.session['member_id'] = member.id
            return redirect("userprofile")

        return render(request, self.template_name, {'form': form})


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        member_id = request.session.get('member_id')
        if not member_id:
            return redirect("index")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        member_id = self.request.session.get('member_id')
        context['member'] = Member.objects.get(id=member_id)

        return context


def logout_view(request):
    request.session.flush()
    return redirect("index")

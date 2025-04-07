from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView
from core.forms import MemberLoginForm
from core.models import Member, Booster


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

    def post(self, request):
        if "booster_id" in request.POST:
            member = request.session.get('member_id')
            booster_id = request.POST["booster_id"]
            booster = get_object_or_404(Booster, id=booster_id)
            opened_cards = booster.open_booster(booster.set_booster, member)

            return render(request, self.template_name, {
                'member': Member.objects.get(id=request.session.get('member_id')),
                'boosters': Booster.objects.all(),
                'opened_cards': opened_cards
            })

    def dispatch(self, request, *args, **kwargs):
        member_id = request.session.get('member_id')
        if not member_id:
            return redirect("index")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        member_id = self.request.session.get('member_id')
        context['member'] = Member.objects.get(id=member_id)
        context['boosters'] = Booster.objects.all()

        return context


def logout_view(request):
    request.session.flush()
    return redirect("index")

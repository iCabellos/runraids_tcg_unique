from django import forms
from django.contrib.auth.hashers import check_password

from core.models import Member, Ability


class MemberLoginForm(forms.Form):
    phone = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    password_member = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        try:
            phone = cleaned_data.get("phone")
            password = cleaned_data.get("password_member")
            member = Member.objects.get(phone=phone)
            if not check_password(password, member.password_member):
                raise forms.ValidationError("Contraseña incorrecta")
        except Member.DoesNotExist:
            raise forms.ValidationError("No se encuentra el número")

        return cleaned_data


class CombatActionForm(forms.Form):
    ability_id = forms.ChoiceField(
        widget=forms.RadioSelect,
        label=""
    )

    def __init__(self, *args, **kwargs):
        hero = kwargs.pop("hero", None)
        super().__init__(*args, **kwargs)

        if hero:
            self.fields["ability_id"].choices = [
                (ability.id, f"{ability.name} ({ability.type}, poder {ability.power})")
                for ability in hero.hero.abilities.all()
            ]

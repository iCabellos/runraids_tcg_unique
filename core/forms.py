from django import forms
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from core.models import BuildingLevelCost, PlayerResource, PlayerBuilding, Banner, Member


class MemberLoginForm(forms.Form):
    phone = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    password_member = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        password = cleaned_data.get("password_member")

        try:
            member = Member.objects.get(phone=phone)
            if not check_password(password, member.password_member):
                raise forms.ValidationError("Contraseña incorrecta")
        except Member.DoesNotExist:
            raise forms.ValidationError("No se encuentra el número")

        return cleaned_data


class CombatActionForm(forms.Form):
    pass


# forms.py
class UpgradeBuildingForm(forms.Form):
    building_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop('member', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        building_id = cleaned_data.get("building_id")

        try:
            building = PlayerBuilding.objects.get(id=building_id, member=self.member)
        except PlayerBuilding.DoesNotExist:
            raise forms.ValidationError("Edificio no encontrado.")

        next_level = building.level + 1
        costs = BuildingLevelCost.objects.filter(building_type=building.building_type, level=next_level)

        for cost in costs:
            player_resource = PlayerResource.objects.filter(
                member=self.member,
                resource_type=cost.resource_type
            ).first()

            if not player_resource or player_resource.amount < cost.amount:
                raise forms.ValidationError(f"Faltan recursos: {cost.resource_type.name}")

        cleaned_data['building'] = building
        cleaned_data['costs'] = costs
        return cleaned_data

    def save(self):
        building = self.cleaned_data['building']
        costs = self.cleaned_data['costs']

        for cost in costs:
            resource = PlayerResource.objects.get(member=self.member, resource_type=cost.resource_type)
            resource.amount -= cost.amount
            resource.save()

        building.level += 1
        building.save()
        return building

class PullForm(forms.Form):
    banner_id = forms.IntegerField(widget=forms.HiddenInput())
    count = forms.IntegerField(
        min_value=1, max_value=10, initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": 1})
    )

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop('member', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        banner_id = cleaned.get("banner_id")
        count = cleaned.get("count") or 1

        try:
            banner = Banner.objects.select_related("cost_resource").get(pk=banner_id, is_active=True)
        except Banner.DoesNotExist:
            raise ValidationError("El banner no existe o no está activo.")

        if not self.member:
            raise ValidationError("Sesión inválida.")

        # Validación suave de saldo (la validación/descarga real es transaccional en el servicio)
        total_cost = int(banner.cost_amount) * int(count)
        pr = PlayerResource.objects.filter(member=self.member, resource_type=banner.cost_resource).first()
        if not pr or pr.amount < total_cost:
            raise ValidationError(f"Saldo insuficiente de {banner.cost_resource.name}. Necesitas {total_cost}.")

        cleaned["banner"] = banner
        cleaned["total_cost"] = total_cost
        return cleaned

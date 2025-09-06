# core/services/pulls.py
from __future__ import annotations
import random
from typing import Optional, Dict, Any, List

from django.db import transaction
from django.db.models import F

from core.models import (
    Member, ResourceType, PlayerResource,
    Hero, PlayerHero,
    Banner, BannerPullLog,
)

class PullError(Exception):
    """Error genérico de tirada."""

class InsufficientCurrency(PullError):
    """No hay recursos suficientes para pagar el coste del pull."""


def _get_or_zero_player_resource(member: Member, resource: ResourceType, for_update: bool = False) -> PlayerResource:
    qs = PlayerResource.objects.filter(member=member, resource_type=resource)
    if for_update:
        qs = qs.select_for_update()
    pr = qs.first()
    if pr:
        return pr
    # No existe fila: creamos en memoria (no salvar aún) para operar con amount=0
    return PlayerResource(member=member, resource_type=resource, amount=0)


@transaction.atomic
def perform_pull(member: Member, banner: Banner, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """
    Ejecuta una tirada completa:
      1) Verifica/Descuenta coste del banner (ResourceType + amount).
      2) Llama a banner.roll_once() para obtener resultado.
      3) Otorga resultado (héroe o recompensas alternativas).
      4) Registra BannerPullLog.
    Devuelve un dict con resumen del resultado y el coste aplicado.

    NOTA sobre 'dupes': si el héroe ya existe, aquí NO se otorga nada extra.
    Lo normal sería convertirlo en fragmentos/token/dupe. Puedes integrar esa
    lógica más adelante (por ejemplo, sumando un recurso “Fragmentos de Héroe”).
    """
    if not banner.is_active:
        raise PullError("El banner no está activo.")

    # 1) Cobro del coste
    cost_res: ResourceType = banner.cost_resource
    cost_amt: int = int(banner.cost_amount or 0)

    if cost_amt <= 0:
        raise PullError("Coste inválido.")

    # Bloqueamos la fila de saldo del jugador para evitar condiciones de carrera
    balance = _get_or_zero_player_resource(member, cost_res, for_update=True)
    if balance.amount < cost_amt:
        raise InsufficientCurrency(f"Saldo insuficiente de {cost_res.name}: {balance.amount} / {cost_amt}")

    # Descuenta
    if balance.pk is None:
        # Si no existía, no puede pagar nada
        raise InsufficientCurrency(f"Saldo insuficiente de {cost_res.name}: 0 / {cost_amt}")
    PlayerResource.objects.filter(pk=balance.pk).update(amount=F('amount') - cost_amt)

    # 2) Tirada
    result = banner.roll_once(rng=rng)

    # 3) Otorgamiento
    log_kwargs = {
        "member": member,
        "banner": banner,
        "result_type": "none",
        "hero": None,
        "reward_snapshot": None,
    }

    if result.get("type") == "hero":
        hero_id = result.get("hero_id")
        is_promo = bool(result.get("promotional"))

        # Crear si no lo tiene; si ya lo tiene, no hacemos nada extra aquí (ver nota de dupes)
        try:
            hero = Hero.objects.get(pk=hero_id)
        except Hero.DoesNotExist:
            raise PullError("El héroe obtenido no existe.")

        # ¿ya lo tiene?
        ph, created = PlayerHero.objects.get_or_create(member=member, hero=hero, defaults={"experience": 0})
        # TODO: si not created -> convertir a fragmentos/dupe en el futuro

        log_kwargs["result_type"] = "hero_promo" if is_promo else "hero_normal"
        log_kwargs["hero"] = hero

        payload = {
            "type": log_kwargs["result_type"],
            "hero": {"id": hero.id, "name": hero.name, "codename": hero.codename},
            "cost": {"resource_type_id": cost_res.id, "amount": cost_amt},
            "owned_before": not created,
        }

    elif result.get("type") == "reward":
        items: List[Dict[str, int]] = result.get("items", [])

        # Sumar cada item al inventario del jugador
        updated = []
        for it in items:
            rt_id = it["resource_type_id"]
            amt = int(it["amount"])
            try:
                rt = ResourceType.objects.get(pk=rt_id)
            except ResourceType.DoesNotExist:
                # si el recurso ya no existe, lo ignoramos o disparamos error según prefieras
                continue

            # upsert + update atómico
            pr, _ = PlayerResource.objects.select_for_update().get_or_create(
                member=member, resource_type=rt, defaults={"amount": 0}
            )
            PlayerResource.objects.filter(pk=pr.pk).update(amount=F('amount') + amt)
            updated.append({"resource_type_id": rt.id, "name": rt.name, "amount": amt})

        log_kwargs["result_type"] = "reward"
        log_kwargs["reward_snapshot"] = updated

        payload = {
            "type": "reward",
            "rewards": updated,
            "cost": {"resource_type_id": cost_res.id, "amount": cost_amt},
        }

    else:
        # Resultado 'none' (caso borde si no hay pools ni recompensas)
        log_kwargs["result_type"] = "none"
        payload = {
            "type": "none",
            "cost": {"resource_type_id": cost_res.id, "amount": cost_amt},
        }

    # 4) Log
    BannerPullLog.objects.create(**log_kwargs)
    return payload

from __future__ import annotations

import urllib.parse

from django.conf import settings


def _digits_only(value: str) -> str:
    return ''.join(ch for ch in (value or '') if ch.isdigit())


def to_e164(raw_phone: str, default_country_code: str | None = None) -> str | None:
    """
    Normaliza un teléfono a formato E.164 (ej: +573001234567).
    - Si viene con indicativo (empieza por 00 o por +), lo respeta.
    - Si viene solo en dígitos, asume PHONE_DEFAULT_COUNTRY_CODE (por defecto 57).
    """
    if not raw_phone:
        return None

    raw_phone = raw_phone.strip()
    default_country_code = default_country_code or getattr(settings, 'PHONE_DEFAULT_COUNTRY_CODE', '57')

    if raw_phone.startswith('+'):
        digits = _digits_only(raw_phone)
        return f'+{digits}' if digits else None

    if raw_phone.startswith('00'):
        digits = _digits_only(raw_phone)
        if len(digits) <= 2:
            return None
        return f'+{digits[2:]}'

    digits = _digits_only(raw_phone)
    if not digits:
        return None

    # Si ya trae el indicativo como dígitos (ej: 57XXXXXXXXXX)
    if digits.startswith(default_country_code):
        return f'+{digits}'

    return f'+{default_country_code}{digits}'


def whatsapp_web_url(*, to_phone: str, text: str) -> str:
    """
    Link para abrir WhatsApp Web con el chat + mensaje listo para enviar.

    Nota: el número "desde el que se envía" lo determina la cuenta que esté logueada en WhatsApp Web
    en el navegador (ej: la sesión del restaurante).
    """
    to_phone_e164 = to_e164(to_phone)
    if not to_phone_e164:
        raise ValueError("Teléfono destino inválido.")

    phone_digits = _digits_only(to_phone_e164)  # WhatsApp espera sin "+"
    encoded_text = urllib.parse.quote(text or '', safe='')
    return f"https://web.whatsapp.com/send?phone={phone_digits}&text={encoded_text}&type=phone_number&app_absent=0"

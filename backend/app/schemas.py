"""
Esquemas Pydantic para request/response del endpoint /search.

Definen el contrato con el frontend y validan/sanitizan el input.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from .config import settings


class SearchRequest(BaseModel):
    """Cuerpo del POST /search."""

    keywords: list[str] = Field(..., min_length=1)
    min_subs: int = Field(default=settings.DEFAULT_MIN_SUBS, ge=0)
    max_subs: int = Field(default=settings.DEFAULT_MAX_SUBS, ge=1)
    language: str = Field(default="es")

    # API key OPCIONAL del usuario. Si viene, se usa solo para esta request
    # y NUNCA se persiste ni se loggea.
    user_api_key: Optional[str] = Field(default=None)

    @field_validator("keywords")
    @classmethod
    def clean_keywords(cls, v: list[str]) -> list[str]:
        # Sanitiza: quita espacios, descarta vacías, recorta a MAX_KEYWORDS,
        # limita longitud y elimina duplicados conservando orden.
        seen = set()
        cleaned: list[str] = []
        for kw in v:
            kw = (kw or "").strip()[:120]
            if not kw:
                continue
            key = kw.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(kw)
            if len(cleaned) >= settings.MAX_KEYWORDS:
                break
        if not cleaned:
            raise ValueError("Debes ingresar al menos una keyword válida.")
        return cleaned

    @field_validator("language")
    @classmethod
    def clean_language(cls, v: str) -> str:
        v = (v or "es").strip().lower()[:5]
        # Solo letras y guion (ej: "es", "en", "es-ES").
        if not v.replace("-", "").isalpha():
            return "es"
        return v

    @field_validator("user_api_key")
    @classmethod
    def clean_api_key(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip()
        # Las API keys de Google son alfanuméricas con - y _. Rechaza basura.
        if not v or len(v) > 100 or not all(c.isalnum() or c in "-_" for c in v):
            return None
        return v


class ChannelResult(BaseModel):
    """Un canal en la respuesta (mismos campos que el CSV del scraper)."""

    nombre: str
    suscriptores: int
    subs_fmt: str
    views: int
    videos: int
    email: str = ""
    instagram: str = ""
    tiktok: str = ""
    twitter: str = ""
    facebook: str = ""
    linkedin: str = ""
    website: str = ""
    canal_url: str
    keyword_origen: str = ""
    descripcion: str = ""


class SearchResponse(BaseModel):
    results: list[ChannelResult]
    total: int
    remaining: Optional[int] = None  # búsquedas gratis restantes (None si usó key propia)
    used_own_key: bool = False


class ErrorResponse(BaseModel):
    detail: str

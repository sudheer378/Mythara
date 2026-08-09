from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.session import Base


class Mythral(Base):
    __tablename__ = "mythrals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(80), index=True)
    mythral_class: Mapped[str] = mapped_column("class", String(80))
    description: Mapped[str] = mapped_column(Text)
    abilities: Mapped[list[str]] = mapped_column(JSON, default=list)
    signature_technique: Mapped[str] = mapped_column(String(200), default="")
    passive_ability: Mapped[str] = mapped_column(String(200), default="")
    stats: Mapped[dict] = mapped_column(JSON, default=dict)
    weaknesses: Mapped[list[str]] = mapped_column(JSON, default=list)
    resistances: Mapped[list[str]] = mapped_column(JSON, default=list)
    habitat: Mapped[str] = mapped_column(String(200), default="")
    evolution: Mapped[dict] = mapped_column(JSON, default=dict)
    bond_system: Mapped[dict] = mapped_column(JSON, default=dict)
    lore: Mapped[str] = mapped_column(Text, default="")
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    audio_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

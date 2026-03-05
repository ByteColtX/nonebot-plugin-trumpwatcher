from __future__ import annotations

from datetime import datetime, timezone

from nonebot_plugin_orm import Model
from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PostArchive(Model):
    __tablename__ = "trumpwatcher_post_archive"

    post_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    content: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(String(255), default="")
    media_text: Mapped[str] = mapped_column(Text, default="")
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class NotifyGroup(Model):
    __tablename__ = "trumpwatcher_notify_group"
    group_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

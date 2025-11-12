"""
ClubMember model - Vereinsmitgliedschaft mit Rollen
"""
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum
from app.models.base import BaseModel


class ClubRole(str, Enum):
    """Roles in a club"""
    OWNER = "owner"  # Vereinsvorsitzender - volle Rechte
    ADMIN = "admin"  # Administrator - fast alle Rechte
    MANAGER = "manager"  # Abteilungsleiter - Management-Rechte
    MEMBER = "member"  # Normales Mitglied - Basis-Rechte
    VOLUNTEER = "volunteer"  # Helfer - limitierte Rechte


class ClubMember(BaseModel):
    """Club membership with roles"""

    __tablename__ = "club_members"

    # Foreign Keys
    club_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Role & Position
    role = Column(
        SQLEnum(ClubRole, name='club_role_enum', values_callable=lambda x: [e.value for e in x]),
        default=ClubRole.MEMBER.value,
        nullable=False
    )
    department = Column(String(100), nullable=True)  # z.B. "Fußball", "Handball"
    position = Column(String(100), nullable=True)  # z.B. "Trainer", "Kassenwart"

    # Additional Info
    notes = Column(String(500), nullable=True)

    # Relationships
    club = relationship("Club", back_populates="members")
    user = relationship("User", back_populates="club_memberships")

    def __repr__(self):
        return f"<ClubMember {self.user_id} in {self.club_id} as {self.role}>"

    @property
    def is_owner(self) -> bool:
        """Check if member is owner"""
        return self.role == ClubRole.OWNER.value or self.role == ClubRole.OWNER

    @property
    def is_admin_or_owner(self) -> bool:
        """Check if member has admin privileges"""
        role_value = self.role.value if isinstance(self.role, Enum) else self.role
        return role_value in ["owner", "admin"]

    @property
    def can_manage(self) -> bool:
        """Check if member can manage club content"""
        role_value = self.role.value if isinstance(self.role, Enum) else self.role
        return role_value in ["owner", "admin", "manager"]
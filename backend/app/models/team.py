from sqlalchemy import Column, Integer, String, Text

from app.core.database import Base


class Team(Base):
    """Jamoa profili.

    `id` — TheSportsDB dagi `idTeam`. Profil ma'lumotlari (stadion, tashkil
    topgan yili, tavsif) deyarli o'zgarmaydi, shuning uchun bir marta olinib
    bazada saqlanadi: jamoa sahifasi har ochilganda tashqi so'rov ketmaydi.
    """

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    # URL uchun: /teams/pakhtakor
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)

    league_id = Column(Integer, index=True, nullable=True)
    league_name = Column(String, nullable=True)

    badge = Column(String, nullable=True)
    stadium = Column(String, nullable=True)
    stadium_capacity = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    country = Column(String, nullable=True)
    founded = Column(Integer, nullable=True)
    website = Column(String, nullable=True)
    # Manbadagi asl tavsif (odatda inglizcha)
    description = Column(Text, nullable=True)
    # AI tarjimasi. Asl matn ham saqlanadi: tarjima tayyor bo'lguncha zaxira
    # bo'lib turadi va kelajakda qayta tarjima qilish imkonini beradi.
    description_uz = Column(Text, nullable=True)

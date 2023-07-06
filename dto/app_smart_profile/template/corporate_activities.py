from dto.app_smart_profile.schema.generic import AppSmartProfileDto


class Activities(AppSmartProfileDto):
    """Шаблоны ответов для апи corporate-activities/activities?typeId={id_corp_activity}"""
    TEAM = [
        {
            "id": 7,
            "name": "Корпоративное мероприятие"
        },
        {
            "id": 23,
            "name": "Тимбилдинг"
        }
    ]
    TEAM_ROLE = [
        {
            "id": 1,
            "name": "Организатор"
        },
        {
            "id": 4,
            "name": "Спикер"
        },
        {
            "id": 2,
            "name": "Участник"
        }
    ]
    CORPORATE_ROLE = [
        {
            "id": 3,
            "name": "Волонтер"
        },
        {
            "id": 1,
            "name": "Организатор"
        },
        {
            "id": 2,
            "name": "Участник"
        }
    ]
    EXPERIENCE_EXCHANGE = [
        {
            "id": 13,
            "name": "Биржа идей"
        },
        {
            "id": 10,
            "name": "Встреча лидеров"
        },
        {
            "id": 11,
            "name": "Гемба"
        },
        {
            "id": 9,
            "name": "Диалог с экспертом"
        },
        {
            "id": 12,
            "name": "Конференция"
        },
        {
            "id": 8,
            "name": "Лидеры учат лидеров"
        },
        {
            "id": 14,
            "name": "Образовательные"
        },
        {
            "id": 22,
            "name": "Стратегическая сессия"
        }
    ]
    EXPERIENCE_EXCHANGE_ROLE = [
        {
            "id": 1,
            "name": "Организатор"
        },
        {
            "id": 5,
            "name": "Преподаватель"
        },
        {
            "id": 4,
            "name": "Спикер"
        },
        {
            "id": 2,
            "name": "Участник"
        }
    ]
    COMPETITIONS = [
        {
            "id": 19,
            "name": "Багатон"
        },
        {
            "id": 21,
            "name": "Брейн-ринг"
        },
        {
            "id": 25,
            "name": "Интеллект-лига"
        },
        {
            "id": 18,
            "name": "Хакатон"
        },
        {
            "id": 20,
            "name": "Что? Где? Когда?"
        }
    ]
    COMPETITIONS_ROLE = [
        {
            "id": 3,
            "name": "Волонтер"
        },
        {
            "id": 1,
            "name": "Организатор"
        },
        {
            "id": 2,
            "name": "Участник"
        }
    ]
    SOCIAL = [
        {
            "id": 17,
            "name": "Благотворительность"
        },
        {
            "id": 16,
            "name": "Волонтерство"
        },
        {
            "id": 15,
            "name": "Донорство"
        },
        {
            "id": 26,
            "name": "Субботник"
        }
    ]
    SOCIAL_ROLE = [
        {
            "id": 3,
            "name": "Волонтер"
        },
        {
            "id": 1,
            "name": "Организатор"
        },
        {
            "id": 2,
            "name": "Участник"
        }
    ]
    SPORT = [
        {
            "id": 3,
            "name": "Туристический слет"
        }
    ]
    SPORT_ROLE = [
        {
            "id": 3,
            "name": "Волонтер"
        },
        {
            "id": 1,
            "name": "Организатор"
        },
        {
            "id": 2,
            "name": "Участник"
        }
    ]
    mapping = {
        "Командные": TEAM,
        "Обмен опытом": EXPERIENCE_EXCHANGE,
        "Соревнование": COMPETITIONS,
        "Социальные": SOCIAL,
        "Спорт": SPORT,
        "Командные (роль)": TEAM_ROLE,
        "Корпоративные (роль)": CORPORATE_ROLE,
        "Обмен опытом (роль)": EXPERIENCE_EXCHANGE_ROLE,
        "Соревнование (роль)": COMPETITIONS_ROLE,
        "Социальные (роль)": SOCIAL_ROLE,
        "Спорт (роль)": SPORT_ROLE,
    }

    def check_json(self, activity_name: str = None) -> list:
        """Получить тело ответа апи для corporate-activities/activities?typeId={id_corp_activity}

        Args:
            activity_name: название корпоративной активности
        """
        return self.mapping[activity_name]

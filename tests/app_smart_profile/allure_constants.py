"""Класс для хранения констант разметки сервисов в allure"""
from allure import epic, feature
from pytest import mark

from clusters import Clusters
from services import Services


@mark.cluster_analytics
@epic(Clusters.ANALYTICS)
class ClusterAnalytics:
    """Разметка сервисов кластера 'Аналитика'."""
    pass


@mark.api
@mark.app_smart_profile
@feature(Services.APP_SMART_PROFILE)
class AppSmartProfileApi(ClusterAnalytics):
    """Разметка сервиса app_smart_profile"""
    pass

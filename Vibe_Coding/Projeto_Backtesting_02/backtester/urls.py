from django.urls import path

from . import views

app_name = "backtester"

urlpatterns = [
    path("", views.home, name="home"),
    path("select-strategy/", views.select_strategy, name="select_strategy"),
    path("apply-filters/", views.apply_filters, name="apply_filters"),
    path("clear-filters/", views.clear_filters, name="clear_filters"),
    path("run-backtest/", views.run_backtest, name="run_backtest"),
]

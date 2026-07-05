from django.urls import path

from . import views

app_name = "backtest"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("backtest/", views.run_backtest, name="run_backtest"),
    path("resultado/<int:pk>/", views.backtest_detail, name="backtest_detail"),
    path("estrategias/", views.strategy_list, name="strategy_list"),
    path("estrategias/nova/", views.strategy_create, name="strategy_create"),
    path("estrategias/<int:pk>/editar/", views.strategy_edit, name="strategy_edit"),
    path("estrategias/<int:pk>/excluir/", views.strategy_delete, name="strategy_delete"),
    path("importar-base/", views.import_base, name="import_base"),
]

from django.core.management.base import BaseCommand

from backtester.data_processor import get_base, get_features, get_strategies, reset_cache


class Command(BaseCommand):
    help = "Pre-carrega a base de dados Bet365 (CSV → DataFrame processado → cache pickle)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Reprocessar CSV mesmo que o cache pickle exista",
        )

    def handle(self, **options):
        force = options["force"]

        if force:
            self.stdout.write("Forcando reprocessamento do CSV...")
            reset_cache()

        self.stdout.write("Carregando base Bet365...")
        df = get_base(force_reprocess=force)

        self.stdout.write(self.style.SUCCESS(
            f"Base carregada: {len(df):,} jogos  |  "
            f"{len(get_strategies(df))} estrategias  |  "
            f"{len(get_features(df))} features"
        ))

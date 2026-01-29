from django.apps import AppConfig


class B2BConfig(AppConfig):
    name = "saleor.b2b"
    verbose_name = "B2B Wholesale"

    def ready(self):
        # Import signals if needed in the future
        pass

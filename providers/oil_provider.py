"""
Модуль кастомного провайдера Faker для нефтяной отрасли.
Содержит генераторы специфичных данных которых нет в стандартном Faker.
"""

from faker.providers import BaseProvider


class OilProvider(BaseProvider):
    """
    Кастомный провайдер Faker для генерации данных нефтяной отрасли.

    Расширяет стандартный Faker специфичными методами генерации
    данных характерных для нефтегазовой промышленности.

    Attributes:
        WELL_TYPES (list): Список допустимых типов скважин.

    Example:
        >>> from faker import Faker
        >>> from providers.oil_provider import OilProvider
        >>> fake = Faker("ru_RU")
        >>> fake.add_provider(OilProvider)
        >>> fake.well_type()
        'нефтяная'
    """

    well_types = ["нефтяная", "газовая", "разведочная", "нагнетальная"]

    def well_type(self) -> str:
        """
        Генерирует случайный тип буровой скважины.

        Выбирает случайный элемент из списка WELL_TYPES используя
        встроенный метод Faker random_element для равномерного распределения.

        Returns:
            str: Тип скважины — одно из значений:
                 'нефтяная', 'газовая', 'разведочная', 'нагнетательная'.

        Example:
            >>> fake.well_type()
            'газовая'
        """

        return self.random_element(self.well_types)

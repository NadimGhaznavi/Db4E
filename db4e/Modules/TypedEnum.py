from enum import Enum
from functools import total_ordering

@total_ordering
class TypedEnum(Enum):
    """
    Enum that enforces member types based on type hints.
    Members compare to their raw values and to members of the
    same enum class only. Cross-enum comparisons are not allowed.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        hints = getattr(cls, "__annotations__", {})
        for member in cls:
            expected = hints.get(member.name)
            if expected and not isinstance(member.value, expected):
                raise TypeError(
                    f"{cls.__name__}.{member.name} = {member.value!r} "
                    f"is not of type {expected.__name__} "
                    f"(got {type(member.value).__name__})"
                )

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return self.value == other  # raw value compare

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.value < other.value
        return self.value < other  # raw value compare
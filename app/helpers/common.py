from enum import Enum, EnumType

def get_enum_values(enum_class: Enum):
    enum_values = []
    
    if isinstance(enum_class, EnumType):
        enum_values = [attribute.value for attribute in enum_class]
    
    return enum_values
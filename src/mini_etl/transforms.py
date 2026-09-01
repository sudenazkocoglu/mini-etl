from typing import Dict, Any, Callable, Optional

class TransformChain:
    def __init__(self, func: Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]) -> None:
        self.func = func

    def process(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.func(record)

    def __rshift__(self, other: "TransformChain") -> "TransformChain":
        def chained(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            res = self.process(record)
            if res is None:
                return None
            return other.process(res)
        return TransformChain(chained)

class MapTransform(TransformChain):
    def __init__(self, mapper: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        super().__init__(mapper)

class FilterTransform(TransformChain):
    def __init__(self, predicate: Callable[[Dict[str, Any]], bool]) -> None:
        def filter_func(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            return record if predicate(record) else None
        super().__init__(filter_func)

class RenameTransform(TransformChain):
    def __init__(self, field_mapping: Dict[str, str]) -> None:
        def rename_func(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            new_record = record.copy()
            for old_key, new_key in field_mapping.items():
                if old_key in new_record:
                    new_record[new_key] = new_record.pop(old_key)
            return new_record
        super().__init__(rename_func)

class CastTransform(TransformChain):
    def __init__(self, type_mapping: Dict[str, Callable[[Any], Any]]) -> None:
        def cast_func(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            new_record = record.copy()
            for key, cast_func_item in type_mapping.items():
                if key in new_record:
                    try:
                        new_record[key] = cast_func_item(new_record[key])
                    except (ValueError, TypeError):
                        return None  # Dönüşüm hatası olursa kaydı düşür
            return new_record
        super().__init__(cast_func)
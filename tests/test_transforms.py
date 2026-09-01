from hypothesis import given, strategies as st
from mini_etl.transforms import MapTransform, FilterTransform, RenameTransform, CastTransform

def test_map_transform():
    t = MapTransform(lambda r: {**r, "age": r["age"] + 1})
    res = t.process({"name": "Ali", "age": 25})
    assert res == {"name": "Ali", "age": 26}

def test_filter_transform():
    t = FilterTransform(lambda r: r["active"] is True)
    assert t.process({"active": True}) == {"active": True}
    assert t.process({"active": False}) is None

def test_rename_transform():
    t = RenameTransform({"fname": "first_name"})
    res = t.process({"fname": "Sudenaz", "age": 20})
    assert res == {"first_name": "Sudenaz", "age": 20}

def test_cast_transform():
    t = CastTransform({"age": int})
    res = t.process({"age": "20"})
    assert res == {"age": 20}

def test_transform_composition_operator():
    # >> operatörü ile zincirleme (composition) testi
    t1 = MapTransform(lambda r: {**r, "x": r["x"] * 2})
    t2 = FilterTransform(lambda r: r["x"] > 10)
    
    pipeline = t1 >> t2
    
    assert pipeline.process({"x": 4}) is None  # 4*2 = 8, 8 > 10 False -> None
    assert pipeline.process({"x": 6}) == {"x": 12}  # 6*2 = 12, 12 > 10 True -> {"x": 12}

@given(st.integers(), st.integers())
def test_property_map_transform(val1: int, val2: int):
    # Hypothesis property-based test 1
    t = MapTransform(lambda r: {"sum": r["a"] + r["b"]})
    res = t.process({"a": val1, "b": val2})
    assert res is not None
    assert res["sum"] == val1 + val2

@given(st.text())
def test_property_rename_transform(text: str):
    # Hypothesis property-based test 2
    t = RenameTransform({"old_key": "new_key"})
    res = t.process({"old_key": text})
    assert res is not None
    assert res.get("new_key") == text

def test_cast_transform_error():
    t = CastTransform({"age": int})
    res = t.process({"age": "invalid_number"})
    assert res is None
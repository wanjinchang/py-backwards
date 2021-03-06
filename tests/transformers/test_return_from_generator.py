import pytest
from py_backwards.transformers.return_from_generator import ReturnFromGeneratorTransformer
from ..utils import transform, run


@pytest.mark.parametrize('before, after', [
    ('''
def fn():
    yield 1
    return 5
    ''', '''
def fn():
    (yield 1)
    _py_backwards_generator_return_0 = StopIteration()
    _py_backwards_generator_return_0.value = 5
    raise _py_backwards_generator_return_0
    '''),
    ('''
def fn():
    if True:
        x = yield from [1]
    return 5
    ''', '''
def fn():
    if True:
        x = (yield from [1])
    _py_backwards_generator_return_0 = StopIteration()
    _py_backwards_generator_return_0.value = 5
    raise _py_backwards_generator_return_0
    ''')])
def test_transform(before, after):
    code = transform(ReturnFromGeneratorTransformer, before)
    assert code == after.strip()


get_value = '''
gen = fn()
next(gen)
val = None
try:
    next(gen)
except StopIteration as e:
    val = e.value
val
'''


@pytest.mark.parametrize('code, result', [
    ('''
def fn():
    yield 1
    return 5
{}
    '''.format(get_value), 5),
    ('''
def fn():
    yield from [1]
    return 6
{}
    '''.format(get_value), 6),
    ('''
def fn():
    x = yield 1
    return 7
{}
    '''.format(get_value), 7),
    ('''
def fn():
    x = yield from [1]
    return 8
{}
    '''.format(get_value), 8)])
def test_run(code, result):
    assert run(ReturnFromGeneratorTransformer, code) == result

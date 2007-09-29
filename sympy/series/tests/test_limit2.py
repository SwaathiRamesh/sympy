from sympy import Symbol, exp, log
from sympy.series.limits2 import compare, mrv, rewrite
from sympy.utilities.pytest import XFAIL

"""
This test suite is testing the limit algoritm using the bottom up approach.
See the documentation in limits2.py. The algorithm itself is highly recursive
by nature, so "compare" is logically the lowest part of the algorithm, yet in
some sense it's the most complex part, because it needs to calculate a limit to
return the result. 
"""

x = Symbol('x')
m = Symbol('m')

def test_compare1():
    assert compare(2, x, x) == "<"
    assert compare(x, exp(x), x) == "<"
    assert compare(exp(x), exp(x**2), x) == "<"
    assert compare(exp(x**2),exp(exp(x)), x) == "<"
    assert compare(1,exp(exp(x)), x) == "<"

    assert compare(x, 2, x) == ">"
    assert compare(exp(x), x, x) == ">"
    assert compare(exp(x**2), exp(x), x) == ">"
    assert compare(exp(exp(x)), exp(x**2), x) == ">"
    assert compare(exp(exp(x)), 1, x) == ">"

    assert compare(2, 3, x) == "="
    assert compare(3, -5, x) == "="
    assert compare(2, -5, x) == "="

    assert compare(x, x**2, x) == "="
    assert compare(x**2, x**3, x) == "="
    assert compare(x**3, 1/x, x) == "="
    assert compare(1/x, x**m, x) == "="
    assert compare(x**m, -x, x) == "="

    assert compare(exp(x), exp(-x), x) == "="
    assert compare(exp(-x), exp(2*x), x) == "="
    assert compare(exp(2*x), exp(x)**2, x) == "="
    assert compare(exp(x)**2, exp(x+exp(-x)), x) == "="
    assert compare(exp(x), exp(x+exp(-x)), x) == "="

    assert compare(exp(x**2), 1/exp(x**2), x) == "="

def test_mrv1():
    assert mrv(x+1/x, x) == set([x])
    assert mrv(x**2, x) == set([x])
    assert mrv(log(x), x) == set([x])
    assert mrv(exp(x), x) == set([exp(x)])
    assert mrv(exp(x**2), x) == set([exp(x**2)])
    assert mrv(exp(x+1/x), x) == set([exp(x+1/x)])
    assert mrv(exp(-x+1/x**2)-exp(x+1/x), x) == set([exp(x+1/x), exp(1/x**2-x)])

def test_mrv2():
    assert mrv(exp(x+exp(-exp(x))), x) == set([exp(-exp(x))])
    assert mrv(exp(x+exp(-x)), x) == set([exp(x+exp(-x)), exp(-x)])
    assert mrv(exp(x+exp(-x**2)), x) == set([exp(-x**2)])
    assert mrv(exp(1/x+exp(-x)), x) == set([exp(-x)])

def test_mrv3():
    assert mrv(exp(x**2)+x*exp(x)+log(x)**x/x, x) == set([exp(x**2)])
    assert mrv(exp(x)*(exp(1/x+exp(-x))-exp(1/x)), x) == set([exp(x), exp(-x)])
    assert mrv(log(x**2+2*exp(exp(3*x**3*log(x)))), x) == set([exp(exp(3*x**3*log(x)))])
    assert mrv(log(x-log(x))/log(x), x) == set([x])
    assert mrv((exp(1/x-exp(-x))-exp(1/x))*exp(x), x) == set([exp(x), exp(-x)])
    assert mrv(1/exp(-x+exp(-x))-exp(x), x) == set([exp(x), exp(-x), exp(x-exp(-x))])
    assert mrv(log(log(x*exp(x*exp(x))+1)), x) == set([exp(x*exp(x))])
    assert mrv(exp(exp(log(log(x)+1/x))), x) == set([x])

def test_mrv4():
    ln = log
    assert mrv((ln(ln(x)+ln(ln(x)))-ln(ln(x)))/ln(ln(x)+ln(ln(ln(x))))*ln(x),
            x) == set([x])
    assert mrv(log(log(x*exp(x*exp(x))+1)) - exp(exp(log(log(x)+1/x))), x) == \
        set([exp(x*exp(x))])

def test_rewrite1():
    e = exp(x)
    assert rewrite(e, mrv(e, x), x, m) == (1/m, -x)
    e = exp(x**2)
    assert rewrite(e, mrv(e, x), x, m) == (1/m, -x**2)
    e = exp(x+1/x)
    assert rewrite(e, mrv(e, x), x, m) == (1/m, -x-1/x)
    e = exp(-x+1/x**2)-exp(x+1/x)
    assert rewrite(e, mrv(e, x), x, m) == (-1/m + m*exp(1/x+1/x**2), -x-1/x)
    e = 1/exp(-x+exp(-x))-exp(x)
    assert rewrite(e, mrv(e, x), x, m) == (1/(m*exp(m))-1/m, -x)

#@XFAIL
#def test_MrvTestCase_page56_ex3_27():
#    # XXX Fails due to infinite recursion
#    expr = exp(-x+exp(-x)*exp(-x*ln(x)))
#    assert mrv(expr,x) == set([exp(x*log(x))])
#    d,md = {},{}
#    r = mrv2(expr,x,d,md)
#    assert set(md.keys()) == set([exp(x*log(x))])

#@XFAIL
#def test_MrvTestCase_page47_ex3_21():
#    h = exp(-x/(1+exp(-x)))
#    expr = exp(h)*exp(-x/(1+h))*exp(exp(-x+h))/h**2-exp(x)+x
#    expected = set([1/h,exp(x),exp(x-h),exp(x/(1+h))])
#    # XXX Incorrect result
#    assert mrv(expr,x).difference(expected) == set()

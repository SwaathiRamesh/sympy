from sympy.functions import sqrt, sign
from sympy.core import S, Wild, Rational, sympify, Mul, Expr
from sympy.core.mul import prod

def sqrtdenest(expr):
    """
    Denests sqrts in an expression that contain other square roots
    if possible, otherwise return the expr unchanged.

    This algorithm is based on
    <http://www.almaden.ibm.com/cs/people/fagin/symb85.pdf>.

    Examples
    ========
    >>> from sympy.simplify.sqrtdenest import sqrtdenest
    >>> from sympy import sqrt
    >>> sqrtdenest(sqrt(5 + 2 * sqrt(6)))
    sqrt(2) + sqrt(3)

    See also: unrad in sympy.solvers.solvers
    """
    expr = sympify(expr)
    if expr.is_Pow and expr.exp is S.Half: #If expr is a square root
        n, d = expr.as_numer_denom()
        if d is S.One:
            return denester([expr])[0]
        else:
            return sqrtdenest(n)/sqrtdenest(d)
    elif isinstance(expr, Expr):
        args = expr.args
        if args:
            return expr.func(*[sqrtdenest(a) for a in args])
    return expr

def denester(nested):
    """
    Denests a list of expressions that contain nested square roots.
    This method should not be called directly - use 'sqrtdenest' instead.
    This algorithm is based on <http://www.almaden.ibm.com/cs/people/fagin/symb85.pdf>.

    It is assumed that all of the elements of 'nested' share the same
    bottom-level radicand. (This is stated in the paper, on page 177, in
    the paragraph immediately preceding the algorithm.)

    When evaluating all of the arguments in parallel, the bottom-level
    radicand only needs to be denested once. This means that calling
    denester with x arguments results in a recursive invocation with x+1
    arguments; hence denester has polynomial complexity.

    However, if the arguments were evaluated separately, each call would
    result in two recursive invocations, and the algorithm would have
    exponential complexity.

    This is discussed in the paper in the middle paragraph of page 179.
    """
    if all((n**2).is_Number for n in nested): #If none of the arguments are nested
        for f in subsets(len(nested)): #Test subset 'f' of nested
            p = prod(nested[i]**2 for i in range(len(f)) if f[i]).expand()
            if 1 in f and f.count(1) > 1 and f[-1]:
                p = -p
            if sqrt(p).is_Number:
                return sqrt(p), f #If we got a perfect square, return its square root.
        return nested[-1], [0]*len(nested) #Otherwise, return the radicand from the previous invocation.
    else:
        a, b, r, R = Wild('a'), Wild('b'), Wild('r'), None
        values = [expr.match(sqrt(a + b * sqrt(r))) for expr in nested]
        if any(v is None for v in values): # this pattern is not recognized
            return nested[-1], [0]*len(nested) #Otherwise, return the radicand from the previous invocation.
        for v in values:
            if r in v: #Since if b=0, r is not defined
                if R is not None:
                    assert R == v[r] #All the 'r's should be the same.
                else:
                    R = v[r]
        if R is None:
            return nested[-1], [0]*len(nested) #return the radicand from the previous invocation.
        d, f = denester([sqrt((v[a]**2).expand()-(R*v[b]**2).expand()) for v in values] + [sqrt(R)])
        if all(fi == 0 for fi in f):
            v = values[-1]
            return sqrt(v[a] + v[b]*d), f
        else:
            v = prod(nested[i]**2 for i in range(len(nested)) if f[i]).expand().match(a+b*sqrt(r))
            if 1 in f and f.index(1) < len(nested) - 1 and f[len(nested)-1]:
                v[a] = -1 * v[a]
                v[b] = -1 * v[b]
            if not f[len(nested)]: #Solution denests with square roots
                vad = (v[a] + d).expand()
                if not vad:
                    return nested[-1], [0]*len(nested) #Otherwise, return the radicand from the previous invocation.
                return (sqrt(vad/2) + sign(v[b])*sqrt((v[b]**2*R/(2*vad)).expand())).expand(), f
            else: #Solution requires a fourth root
                FR, s = (R.expand()**Rational(1,4)), sqrt((v[b]*R).expand()+d)
                return (s/(sqrt(2)*FR) + v[a]*FR/(sqrt(2)*s)).expand(), f

def subsets(n):
    """
    Returns all possible subsets of the set (0, 1, ..., n-1) except the empty,
    listed in numerical order according to binary representation.

    Examples
    ========
    >>> from sympy.simplify.sqrtdenest import subsets
    >>> subsets(3)
    [[0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]
    """
    binary = lambda x: x>0 and binary(x>>1) + [x&1] or []
    pad = lambda l: [0]*(n-len(l)) + l #Always returns a list of length 'n'
    return [pad(binary(i)) for i in range(1, 2**n)]

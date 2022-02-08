![FPy](https://github.com/Z-Shang/fpy/blob/c60c60d16127723fcc4e30683de1ba39190f4467/fpy.png)

[![version_badge](https://img.shields.io/pypi/v/fppy.svg)](https://pypi.org/project/fppy/0.0.1/)
# Functional Python

For better computation composing in Python

## Goals
* To bring the ability of composing computations in the functional way
* Make my life easier

## No Goals
* Exact clone of Haskell
* Blazing fast / super efficient

## Python is Already Amazing, Why Bother?
* Because I can
* Python may be amazing in some field, but sucks from the functional perspective

## Python Sucks, Why Bother?
* Because I can
* Python is still used in my work place

## Install
With pip:
> pip install fppy

## Control:
### Functor `fpy.control.functor`
Given Functors `f`, `g`:
* `__fmap__ :: f a -> (a -> b) -> f b`
* `__ntrans__ :: f a -> (f a ~> g b) -> g b`

#### Operators:
* `|` = `__fmap__`
* `&` = `__ntrans__`

#### Functions:
* `fmap` = `__fmap__`

### NTrans (Natrual Transform) `fpy.control.natural_transform`
Given Functors `f`, `g`:
* `__trans__ :: f a ~> g b`

### Applicative : Functor `fpy.control.applicative`
No new trait comparing to functor, `liftA2` is defined using `fmap`

### Monad : Applicative `fpy.control.monad`
Given Monad `m`:
* `__bind__ :: m a -> (a -> m b) -> m b`

#### Operators:
* `>>` = `__bind__`

#### Do Notation:
* `@do(Monad)` enables do notation in the decorated function, where the explicit `return` statement will be treated as `ret` from the given `Monad` type, if no `return` statement is given, the last element on the stack will be returned.
* `name <- computation` binds the computation to the following block, calling the `__bind__` method of the monad object returned from `computation` with the name `name`.
* `(name1, name2, ..., namen) <- computation` works in the similar way as the single name binding, this applys the binding function to the tuple contained within the monad object instead of calling the function directly.
* `name1, name2, ..., namen <- computation` same as above

## Data
### Maybe : Monad `fpy.data.maybe`
#### Types:
* `Maybe[T]`
* `Just[T] : Maybe[T]`
* `Nothing[T] : Maybe[T]`
#### Functions:
* `isJust :: Maybe[T] -> bool`
* `isNothing :: Maybe[T] -> bool`
* `fromJust :: Maybe[T] -> T`
* `fromMaybe :: T -> Maybe[T] -> T`
* `maybe :: S -> (T -> S) -> Maybe[T] -> S`
* `mapMaybe :: (T -> Maybe[S]) -> List[T] -> List[S]`

### Either : Monad `fpy.data.either`
#### Types:
* `Either[T]`
* `Left[T] : Either[T]`
* `Right[T] : Either[T]`

### Forgetful : Monad (Forgetful Functor) `fpy.data.forgetful`
#### Types:
* `Under[T]`
`Under` similar to Haskell's `Identity` monad

### Cont : Monad `fpy.data.cont`
#### Types:
* `Cont[T, R]`

#### Functions:
* `cont :: (A -> B) -> Cont[A, B]`
* `runCont :: Cout[B, C] -> C`

#### Functions:
Given functor `f`:
`forget: NTrans[F, B, Under, T] :: f b ~> Under[T]`


### Utility Functions `fpy.data.function`
* `id_ :: T -> T`
* `const :: T -> A -> T`
* `flip :: (B -> A -> T) -> A -> B -> T`
* `fix :: (A -> A) -> A`
* `on :: (B -> B -> T) -> (A -> B) -> A -> A -> T`

## Composable
### Composable `fpy.composable.composable`
* `__compose__`
#### Operators:
* `^` = `__compose__`

### Transparent `fpy.composable.transparent`
* `__underlying__`
Delegate an attribute access to an underlying object

### Function `fpy.composable.function`
#### Types:
* `func : Composable`
* `SignatureMismatchError`
* `NotEnoughArgsError`

### Collections `fpy.composable.collections`
#### Types:
* `Seq : func`
* `Map : func`

#### Functions:
* `transN(n, f, it) := it[n] = f(it[n])`
* `getN(n, it) := it[n]`
* `setN(n, v, it) := it[n] = v`
* `eqN(n, it, x) := it[n] == x`
* `mapN(n, fn, lsts) := map(fn, zip(lst1, lst2 ... lstn))`
* `of_(v1 ... vn) := _ in (v1 ... vn)`
* `is_(t) := isinstance(_, t)`
* `and_(a, b) := a(_) and b(_)`
* `or_(a, b) := a(_) or b(_)`
* `to(dst, src) := dst(src)`
* `apply(fn) := fn(*a, **k)`
* `fwd_ = Under.ret`

#### Predefined Vars:
* `trans0`
* `trans1`
* `get0`
* `get1`
* `set0`
* `set1`
* `eq0`
* `eq1`
* `mp1`
* `mp2`

## Parsec
### Parsec `fpy.parsec.parsec`
#### Types:
* `parser[S, T] :: [S] -> Either [S] ([T] * [S])`

#### Operators:
* `*` = `parser.timeN`
* `+` = `parser.concat`
* `|` = `parser.choice`
* `>>` = `parser.parseR`
* `<<` = `parser.parseL`

#### Functions:
* `one :: (S -> bool) -> parser[S, S]`
* `neg :: (S -> bool) -> parser[S, S]`
* `just_nothing :: parser[S, T]`
* `pmaybe :: parser[S, T] -> parser[S, T]`
* `many :: parser[S, T] -> parser[S, T]`
* `many1 :: parser[S, T] -> parser[S, T]`
* `ptrans :: parser[S, T] -> (T -> Y) -> parser[S, Y]`
* `peek :: parser[S, T] -> parser[S, T]`
* `skip :: parser[S, T] -> parser[S, T]`
* `pseq :: [S] -> parser[S, T]`
* `inv :: parser[S, T] -> parser[S, T]`

## Dependencies
* [bytecode](https://github.com/MatthieuDartiailh/bytecode)

## License
GPL3+

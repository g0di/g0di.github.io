Title: Don't use Python's property (for bad reasons)
Tags: python, good-practices
Description: Explain when and how you should use Python property descriptor

# Don't use Python's property (for bad reasons)

I recently stumbled upon a code from one of my coworker who is rather new to Python. He is coming from a Java/Scala background and used python's `property` decorator to mimic Java Getters/Setters. Let's see why you should not do this.

```python
class ParquetReader:
    def __init__(self, spark_session):
        self._spark_session = spark_session

    @property
    def spark_session(self):
        return self._spark_session
```

This made me think about [this article](https://www.b-list.org/weblog/2023/dec/21/dont-use-python-property/) which outline pretty well the reason why you should not do this in Python.

The TL;DR is: _"It is not Pythonic"_. Don't blindly apply what you've seen in other languages like Java directly into Python.

## Avoid exposing your objects internals

First, you should not expose your object internals except if it is a data class (i.e: A structure for holding pure data without behavior; by the way, you should not create objects mixing both data and behavior).

The reason is that it may cause client code to use those internals, creating strong coupling between each other and greatly reducing your ability to refactor your code. If that case arise (using another object's internals), it might be the sign of a [Feature Envy](https://refactoring.guru/fr/smells/feature-envy) code smell. You can try the [Tell Don't Ask](https://deviq.com/principles/tell-dont-ask) principle as well to help you mitigate this.

## Use `property` for dynamic computations on the fly

The main purpose of the `property` decorator is to allow you to perform additional computations when reading/writing/deleting an attribute. If there is no additional behavior, just stick to the raw attribute directly.

```python
# Details for observer object is omitted
class Foo:
    def __init__(self, observer):
        self._bar = ""
        self.observer = observer

    @property
    def bar(self):
        return self._bar

    @bar.setter
    def bar(self, value):
        self._bar = value
        self.observer.notify(f"bar updated: {self.bar}")
```

## Use `property` for refactoring without breaking changes

Another reason to use that decorator is if you plan on changing the attribute name without introducing breaking change.

```python
class ParquetReader:
    def __init__(self, spark_session):
        self._session = spark_session

    @property
    def spark_session(self):
        return self._session
```

Here we can safely rename our internal attribute without changing the one exposed.

## Do not use `property` for aesthetic reasons

You should not use the `property` decorator to turns a real function into a simple attribute just because it looks nicer in particular if this function is doing some heavy computation (or at least, non neglictible one). Otherwise, clients might be tempted to use repeatedly this "attribute" causing performances issues

```python
# Bad
class Circle:

    @property
    def area(self) -> float:
        ...

# Good
class Circle:

    def area(self) -> float:
        ...
```

# coding: utf-8
# # using mypy linter
# flake8: noqa
from __future__ import annotations
import asyncio
import datetime
from contextvars import ContextVar, copy_context
from dataclasses import dataclass
from typing import Any, Text, Optional


# # __future__ annotations allow forward referencing
class NeedsForwardReference:

    def __init__(self) -> None:
        self.var = var = ContextVar('context', default=42)
        self.ctx = copy_context()
        self.test: Optional[int] = None

    @classmethod
    def create_dataclass(cls, i: int) -> DataClass:
        return DataClass(x=i)

    def validate_dataclass(self, obj: DataClass,
                           var: Optional[str] = None) -> bool:
        okay = True
        # # too simple attempt to dynamically check typing definitions ...
        for k, v in obj.__dataclass_fields__.items():  # type: ignore
            typ = v.type  # type: ignore
            if (var is None or var == k  # type: ignore
                ) and typ != 'Any' and '[' not in typ:  # type: ignore
                # # How to do this without eval?
                okay &= isinstance(getattr(obj, k), eval(typ))  # type: ignore
        return okay

    async def display_dt(self, t_end: float = 5.0) -> None:
        loop = asyncio.get_running_loop()  # type: ignore
        end_time = loop.time() + t_end  # type: ignore

        # # context test
        def test_ctx() -> None:
            self.var.set(0)

        # #
        while True:
            print(datetime.datetime.now())
            if (loop.time() + 1.0) >= end_time:  # type: ignore
                self.ctx.run(test_ctx)
                self.test = self.ctx[self.var]
                # #
                print('orig:', self.var.get(), 'ctx:', self.test)
                #
                break
            await asyncio.sleep(1)


# # dataclasses and typing
@dataclass  # type: ignore
class DataClass:
    x: int
    y: Any = None  # type: ignore
    z: int = 5
    a: Optional[Text] = None

    def add_one_to_x(self) -> None:
        try:
            self.x += 1
        except TypeError as err:
            print(err)
            breakpoint()  # Breakpoint


if __name__ == '__main__':

    # # SyntaxError!
    # await = None
    # async = None

    cls = NeedsForwardReference()
    print(cls.var)

    c = cls.create_dataclass(0)
    c.add_one_to_x()
    if not cls.validate_dataclass(c):
        print('Oooops.')

    c2 = DataClass(x=0, y=1)

    if c2.a is None:
        c2.a = 'a'

    # # wrong type!
    c2.x = 'x'
    c2.add_one_to_x()
    if not cls.validate_dataclass(c2, 'x'):
        print(f'Type {type(c2.x)} for {c2}.x is wrong.')

    # # dictionary order
    testd = dict.fromkeys(range(3), 'fromkeys')
    testd[3] = 'assigned'
    for k, v in testd.items():
        print(k, v)
    print(*[testd.popitem() for k in testd.copy()])

    asyncio.run(cls.display_dt(t_end=3))  # type: ignore

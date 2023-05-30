import random
import string
from collections.abc import MutableMapping, Iterator
from dataclasses import dataclass, field
from typing import Any, TypeVar

from app.api.resources.model import Model
from app.api.resources.results import ResultItem
from app.api.resources.status import Status

KT = TypeVar('KT', bound=str)
VT = TypeVar('VT', bound=tuple[Model, list[ResultItem] | None])


def _make_results() -> list[ResultItem]:
    results = []
    for idx in range(random.randint(0, 15)):
        results.append(ResultItem(cluster=idx,
                                  occurrences=random.randint(1, 1000),
                                  members=[''.join(random.choices(string.ascii_uppercase, k=10)) for _ in
                                           range(random.randint(1, 6))])
                       )
    return results


@dataclass
class ModelStore(MutableMapping[KT, VT]):
    _data: dict[KT, VT] = field(default_factory=dict, init=False)

    def set_status(self, model_id: KT, status: Status) -> None:
        if model_id not in self:
            raise KeyError(f'No model with id {model_id!r} exists')
        if (model := self[model_id][0]).status in (Status.FAILED, Status.COMPLETED):
            raise ValueError('A model that has failed or completed cannot have its status changed')
        model.status = status

    def get_results(self, model_id: KT) -> list[ResultItem] | None:
        if self[model_id][0].status != Status.COMPLETED:
            return None
        if not (results := self[model_id][1]):
            results = _make_results()
            self[model_id] = (self[model_id][0], results)
        return results

    def get(self, model_id: KT) -> VT | None:
        if model_id in self:
            return self[model_id]
        return None

    def __setitem__(self, model_id: KT, value: VT) -> None:
        if isinstance(value, tuple):
            self._data[model_id] = value
            return
        if model_id in self:
            raise KeyError(f'Duplicate keys are not allowed')
        elif model_id != str(value.id):
            raise ValueError('The \'model_id\' must match the ID of the model.')
        self._data[model_id] = (value, None)

    def __delitem__(self, model_id: KT) -> None:
        del self._data[model_id]

    def __getitem__(self, model_id: KT) -> VT:
        return self._data[model_id]

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, item: Any) -> bool:
        return item in self._data

    def __iter__(self) -> Iterator[KT]:
        return iter(self._data)

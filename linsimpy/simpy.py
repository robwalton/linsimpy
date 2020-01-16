from simpy.resources.store import FilterStore, FilterStoreGet
from simpy.core import BoundClass


class FilterStoreGetWithRemove(FilterStoreGet):

    def __init__(self, resource, filter=lambda item: True):
        self.remove_item = True
        super(FilterStoreGetWithRemove, self).__init__(resource, filter)


class FilterStoreGetWithNoRemove(FilterStoreGet):

    def __init__(self, resource, filter=lambda item: True):
        self.remove_item = False
        super(FilterStoreGetWithNoRemove, self).__init__(resource, filter)


class ReadableFilterStore(FilterStore):
    """Extends simpy.resources.store.FilterStore with a non-destructive read()
    method."""

    get = BoundClass(FilterStoreGetWithRemove)

    read = BoundClass(FilterStoreGetWithNoRemove)

    def _do_get(self, event):
        for item in self.items:
            if event.filter(item):
                if event.remove_item:
                    self.items.remove(item)
                event.succeed(item)
                break
        return True

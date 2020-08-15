"""
The game loop consists of Entities taking Actions. Actions have a wind-up time measured in
Time Units (TU). Each iteration of the main loop (tick), all entities contribute a number of TUs to their
current action's wind-up. Whenever an Entity completes its Action's wind-up, the Action is resolved.

Actions may be interrupted by another Action that resolves during their wind-up, possibly replacing the current action
with a new one that must be taken.

Certain actions may actually be a sequence of actions that must be done in order. The sequence of actions
may be modified as the sequence resolves, for example, to append new actions to the end.
"""
from __future__ import annotations

import heapq
from functools import total_ordering
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Iterable, MutableMapping, List, Any
if TYPE_CHECKING:
    pass


# noinspection PyMethodMayBeStatic
class Action(ABC):
    name = 'Action'

    owner: Entity = None
    loop: ActionLoop = None
    start_tick: float = None

    @abstractmethod
    def get_windup_duration(self) -> float:
        """Return the windup duration, in TU"""
        ...

    def is_active(self) -> bool:
        return self.loop is not None

    def setup(self, owner: Entity, loop: ActionLoop) -> None:
        """Called by the action loop to prepare the Action to be scheduled."""
        self.owner = owner
        self.loop = loop
        self.start_tick = loop.get_tick()

    def started(self) -> None:
        """Called when the action has been scheduled"""
        pass

    def get_remaining_windup(self) -> float:
        if not self.is_active():
            return self.get_windup_duration()
        return self.loop.get_remaining_windup(self)

    def get_elapsed_windup(self) -> float:
        if not self.is_active():
            return 0
        return self.loop.get_tick() - self.start_tick

    def can_resolve(self) -> bool:
        """Return True if the action can be resolved.
        Called to determine whether an Entity can actually take a given action."""
        return True

    @abstractmethod
    def resolve(self) -> Optional[Action]:
        """Called to resolve the action.
        Optionally returns an Action that must be performed next."""
        ...

    def resolve_failed(self) -> Optional[Action]:
        """Called when an action could not be resolved.
        Optionally returns an Action that must be performed next."""
        return None

    force_next: Action = None
    def set_force_next(self, next: Action) -> None:
        self.force_next = next

    # def can_interrupt(self, other: 'Action') -> bool:
    #     """Return True if this action can be interrupted by another."""
    #     return True
    #
    # def interrupted_by(self, other: 'Action') -> None:
    #     """Called when an action is interrupted."""
    #     pass

    def __repr__(self) -> str:
        if self.is_active():
            return f'<{self.__class__.__name__} owned by: {self.owner}, started: {self.start_tick}, remaining: {self.get_remaining_windup()}>'
        return f'<{self.__class__.__name__}: unbound action>'


## generator based action sequences???
# class ActionSequence(Action):
#     current_action: Action = None
#
#     @abstractmethod
#     def get_next_action(self) -> Optional[Action]:
#         ...
#
#     def base_windup(self) -> float:
#         return self.current_action.base_windup()
#
#     def setup_action(self, owner: 'Entity', loop: 'ActionLoop') -> None:

class Entity:
    loop: ActionLoop = None

    @property
    def tiebreaker_priority(self) -> float:
        return 0

    def set_action_loop(self, loop: Optional[ActionLoop]):
        if self.loop != loop:
            if self.loop is not None:
                self.loop.remove_entity(self)
            if loop is not None:
                self.loop = loop
                self.loop.add_entity(self)

    def get_current_action(self) -> Optional[Action]:
        return self.loop.get_current_action(self)

    def set_current_action(self, action: Optional[Action]) -> None:
        if action is not None:
            self.loop.schedule_action(self, action)
        elif (current := self.get_current_action()) is not None:
            self.loop.cancel_action(current)


# ActionLoop
@total_ordering
class ActionQueueItem:
    windup: int
    action: Action

    def __init__(self, windup: int, action: Action):
        self.windup = windup
        self.action = action

    def elapse(self, amount: int) -> None:
        self.windup -= amount

    @property
    def _sort_key(self) -> Any:
        return self.windup, -self.action.owner.tiebreaker_priority

    def __eq__(self, other: ActionQueueItem) -> bool:
        return self._sort_key == other._sort_key
    def __lt__(self, other: ActionQueueItem) -> bool:
        return self._sort_key < other._sort_key

class ActionLoop:
    entity_actions: MutableMapping[Entity, Optional[Action]]
    queue_items: MutableMapping[Action, ActionQueueItem]
    action_queue: List[ActionQueueItem]
    def __init__(self):
        self.elapsed = 0  # in TU
        self.entity_actions = {}
        self.action_queue = []
        self.queue_items = {}

    def get_tick(self) -> int:
        return self.elapsed

    def add_entity(self, entity: Entity) -> None:
        self.entity_actions.setdefault(entity)

    def remove_entity(self, entity: Entity) -> None:
        if entity in self.entity_actions:
            action = self.entity_actions[entity]
            if action is not None:
                self.cancel_action(action)
            del self.entity_actions[entity]

    def get_entities(self) -> Iterable[Entity]:
        return iter(self.entity_actions.keys())

    def get_idle_entities(self) -> Iterable[Entity]:
        return (entity for entity, action in self.entity_actions.items() if action is None)

    def is_entity_idle(self, entity: Entity) -> bool:
        return self.entity_actions[entity] is None

    def queued_action_count(self) -> int:
        return len(self.action_queue)

    def get_current_action(self, entity: Entity) -> Optional[Action]:
        return self.entity_actions[entity]

    def get_remaining_windup(self, action: Action) -> Optional[float]:
        item = self.queue_items.get(action, None)
        if item is not None:
            return item.windup
        return None

    def schedule_action(self, entity: Entity, action: Action) -> None:
        prev_action = self.entity_actions.get(entity)
        if prev_action is not None:
            self.cancel_action(prev_action)

        action.setup(entity, self)
        windup = action.get_windup_duration()

        self.entity_actions[entity] = action
        item = ActionQueueItem(round(windup), action)
        self.queue_items[action] = item
        heapq.heappush(self.action_queue, item)
        action.started()

    def cancel_action(self, action: Action):
        entity = action.owner
        if entity is not None and self.entity_actions[entity] == action:
            self.entity_actions[entity] = None
        item = self.queue_items.pop(action)
        self.action_queue.remove(item)
        heapq.heapify(self.action_queue)

    def resolve_next(self) -> None:
        if len(self.action_queue) == 0:
            return  # nothing scheduled

        item = heapq.heappop(self.action_queue)
        elapsed, current_action = item.windup, item.action
        del self.queue_items[current_action]
        self.elapsed += elapsed

        # first, update the windup counters of all other actions
        # since this does not change the ordering, this can be done by efficiently rebuilding the queue
        for item in self.action_queue:
            item.elapse(elapsed)

        # next, resolve the current action
        entity = current_action.owner
        if current_action.can_resolve():
            next_action = current_action.resolve()
        else:
            next_action = current_action.resolve_failed()
        self.entity_actions[entity] = None

        force_next = current_action.force_next
        if force_next is not None:
            force_next.set_force_next(next_action)
            next_action = force_next

        if next_action is not None:
            self.schedule_action(entity, next_action)

        # recheck can_resolve on all other actions
        for action in list(self.queue_items.keys()):
            if not action.can_resolve():
                self.cancel_action(action)

# MeleeEngagement
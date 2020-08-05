"""
The game loop consists of Entities taking Actions. Actions have a wind-up time measured in
Time Units (TU). Each iteration of the main loop (tick), all entities contribute a number of TUs to their
current action's wind-up. Whenever an Entity completes its Action's wind-up, the Action is resolved.

Actions may be interrupted by another Action that resolves during their wind-up, possibly replacing the current action
with a new one that must be taken.

Certain actions may actually be a sequence of actions that must be done in order. The sequence of actions
may be modified as the sequence resolves, for example, to append new actions to the end.
"""

import heapq
from abc import ABC, abstractmethod
from typing import Optional, Iterable, NamedTuple, MutableMapping, List


# noinspection PyMethodMayBeStatic
class Action(ABC):
    name = 'Action'

    owner: 'Entity' = None
    loop: 'ActionLoop' = None

    @abstractmethod
    def get_base_windup(self) -> float:
        """Return the windup duration, in TU"""
        ...

    def setup(self, owner: 'Entity', loop: 'ActionLoop') -> None:
        """Called by the action loop to prepare the Action to be scheduled."""
        self.owner = owner
        self.loop = loop

    def can_resolve(self) -> bool:
        """Return True if the action can be resolved.
        Called to determine whether an Entity can actually take a given action."""
        return True

    def started(self) -> None:
        """Called when the action has been scheduled"""
        pass

    def get_remaining_windup(self) -> float:
        return self.loop.get_remaining_windup(self)

    @abstractmethod
    def resolve(self) -> Optional['Action']:
        """Called to resolve the action.
        Optionally returns an Action that must be performed next."""
        ...

    def resolve_failed(self) -> Optional['Action']:
        """Called when an action could not be resolved.
        Optionally returns an Action that must be performed next."""
        return None

    # def can_interrupt(self, other: 'Action') -> bool:
    #     """Return True if this action can be interrupted by another."""
    #     return True
    #
    # def interrupted_by(self, other: 'Action') -> None:
    #     """Called when an action is interrupted."""
    #     pass


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
    def __init__(self, loop: 'ActionLoop'):
        self.loop = loop

    def get_action_rate(self) -> float:
        """Allows actions to be performed quicker or slower for different entities."""
        return 1.0

    def idle(self) -> None:
        """Called when an Entity is idle"""
        return None

    def get_current_action(self) -> Optional[Action]:
        return self.loop.get_current_action(self)

    def set_current_action(self, action: Action) -> None:
        self.loop.schedule_action(self, action)

# ActionLoop
class ActionQueueItem(NamedTuple):
    windup: float
    action: Action

    def elapse(self, amount: float) -> 'ActionQueueItem':
        return ActionQueueItem(self.windup - amount, self.action)

class ActionLoop:
    entity_actions: MutableMapping[Entity, Optional[Action]]
    queue_items: MutableMapping[Action, ActionQueueItem]
    action_queue: List[ActionQueueItem]
    def __init__(self):
        self.elapsed = 0  # in TU
        self.entity_actions = {}
        self.action_queue = []
        self.queue_items = {}

    def get_entities(self) -> Iterable[Entity]:
        return iter(self.entity_actions.keys())

    def get_idle_entities(self) -> Iterable[Entity]:
        return (entity for entity, action in self.entity_actions.items() if action is None)

    def is_entity_idle(self, entity: Entity) -> bool:
        return self.entity_actions[entity] is None

    def get_current_action(self, entity: Entity) -> Optional[Action]:
        return self.entity_actions[entity]

    def get_remaining_windup(self, action: Action) -> Optional[float]:
        item = self.queue_items.get(action, None)
        if item is not None:
            return item.windup
        return None

    def schedule_action(self, entity: Entity, action: Action) -> None:
        prev_action = self.entity_actions.get(entity, None)
        if prev_action is not None:
            self.cancel_action(prev_action)

        action.setup(entity, self)
        windup = action.get_base_windup() / entity.get_action_rate()

        self.entity_actions[entity] = action
        item = ActionQueueItem(windup, action)
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

    def process_idle_entities(self) -> None:
        for entity in self.get_idle_entities():
            entity.idle()

    def resolve_next(self) -> None:
        if len(self.action_queue) == 0:
            return  # nothing scheduled

        item = heapq.heappop(self.action_queue)
        elapsed, current_action = item.windup, item.action
        del self.queue_items[current_action]
        self.elapsed += elapsed

        # first, update the windup counters of all other actions
        # since this does not change the ordering, this can be done by efficiently rebuilding the queue
        self.action_queue = [ item.elapse(elapsed) for item in self.action_queue ]

        # next, resolve the current action
        entity = current_action.owner
        if current_action.can_resolve():
            next_action = current_action.resolve()
        else:
            next_action = current_action.resolve_failed()
        self.entity_actions[entity] = None

        if next_action is not None:
            self.schedule_action(entity, next_action)

# MeleeEngagement
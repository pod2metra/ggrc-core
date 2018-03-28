# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>


class UserPermissions(object):
    """Interface required for extensions providing user rights information for
  role-based access control.
  """

    def is_allowed_create(self, resource_type, resource_id, context_id):
        """Whether or not the user is allowed to create a resource of the specified
    type in the context."""
        raise NotImplementedError()

    def is_allowed_read(self, resource_type, resource_id, context_id):
        """Whether or not the user is allowed to read a resource of the specified
    type in the context."""
        raise NotImplementedError()

    def is_allowed_read_for(self, instance):
        """Whether or not the user is allowed to read this particular resource
    instance. This is in contrast to ``is_allowed_read`` which checks that the
    user can read resources of this type, though may not be able to read any
    one particular instance depending upon permissions implementation.
    """
        raise NotImplementedError()

    def is_allowed_update(self, resource_type, resource_id, context_id):
        """Whether or not the user is allowed to update a resource of the specified
    type in the context."""
        raise NotImplementedError()

    def is_allowed_update_for(self, instance):
        """Whether or not the user is allowed to update this particular resource
    instance. This is in contrast to ``is_allowed_update`` which checks that
    the user can update resources of this type, though may not be able to
    update any one particular instance depending upon permissions
    implementation.
    """
        raise NotImplementedError()

    def is_allowed_delete(self, resource_type, resource_id, context_id):
        """Whether or not the user is allowed to delete a resource of the specified
    type in the context."""
        raise NotImplementedError()

    def is_allowed_delete_for(self, instance):
        """Whether or not the user is allowed to delete this particular resource
    instance. This is in contrast to ``is_allowed_delete`` which checks that
    the user can delete resources of this type, though may not be able to
    delete any one particular instance depending upon permissions
    implementation.
    """
        raise NotImplementedError()

    def create_contexts_for(self, resource_type):
        """All contexts in which the user has create permission."""
        raise NotImplementedError()

    def read_contexts_for(self, resource_type):
        """All contexts in which the user has read permission."""
        raise NotImplementedError()

    def update_contexts_for(self, resource_type):
        """All contexts in which the user has update permission."""
        raise NotImplementedError()

    def delete_contexts_for(self, resource_type):
        """All contexts in which the user has delete permission."""
        raise NotImplementedError()


class BasicUserPermissions(UserPermissions):
    """Basic implementation of a UserPermissions object."""

    def __init__(self,
                 create_contexts=None,
                 read_contexts=None,
                 update_contexts=None,
                 delete_contexts=None):
        """Args:
      create_contexts (dict of (resource_type,[context_id])): The contexts
        where the user is allowed to create a resource of a given type.

      read_contexts (dict of (resource_type,[context_id])): The contexts
        where the user is allowed to read a resource of a given type.

      update_contexts (dict of (resource_type,[context_id])): The contexts
        where the user is allowed to update a resource of a given type.

      delete_contexts (dict of (resource_type,[context_id])): The contexts
        where the user is allowed to delete a resource of a given type.
    """
        self.create_contexts = create_contexts or {}
        self.read_contexts = read_contexts or {}
        self.update_contexts = update_contexts or {}
        self.delete_contexts = delete_contexts or {}

    def is_allowed_create(self, resource_type, resource_id, context_id):
        """Whether or not the user is allowed to create a resource of the specified
    type in the context."""
        return resource_type in self.create_contexts and \
            context_id in self.create_contexts[resource_type]

    def is_allowed_read(self, resource_type, resource_id, context_id):
        """Whether or not the user is allowed to read a resource of the specified
    type in the context."""
        return resource_type in self.read_contexts and \
            context_id in self.read_contexts[resource_type]

    def is_allowed_update(self, resource_type, resource_id, context_id):
        """Whether or not the user is allowed to update a resource of the specified
    type in the context."""
        return resource_type in self.update_contexts and \
            context_id in self.update_contexts[resource_type]

    def is_allowed_delete(self, resource_type, resource_id, context_id):
        """Whether or not the user is allowed to delete a resource of the specified
    type in the context."""
        return resource_type in self.delete_contexts and \
            context_id in self.delete_contexts[resource_type]

    def is_allowed_delete_for(self, instance):
        return True

    def create_contexts_for(self, resource_type):
        """All contexts in which the user has create permission."""
        return self.create_contexts.get(resource_type) or []

    def read_contexts_for(self, resource_type):
        """All contexts in which the user has read permission."""
        return self.read_contexts.get(resource_type) or []

    def update_contexts_for(self, resource_type):
        """All contexts in which the user has update permission."""
        return self.update_contexts.get(resource_type) or []

    def delete_contexts_for(self, resource_type):
        """All contexts in which the user has delete permission."""
        return self.delete_contexts.get(resource_type) or []

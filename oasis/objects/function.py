# coding=utf-8
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_versionedobjects import fields

from oasis.common import exception
from oasis.common import utils
from oasis.db import api as dbapi
from oasis.objects import base
from oasis.objects import fields as m_fields


@base.OasisObjectRegistry.register
class Function(base.OasisPersistentObject, base.OasisObject,
          base.OasisObjectDictCompat):
    # Version 1.0: Initial version
    VERSION = '1.0'

    dbapi = dbapi.get_instance()

    fields = {
        'id': fields.IntegerField(),
        'name': fields.StringField(nullable=True),
        'project_id': fields.StringField(nullable=True),
        'user_id': fields.StringField(nullable=True),
        'stack_id': fields.StringField(nullable=True),
        'status': m_fields.FunctionStatusField(nullable=True),
        'status_reason': fields.StringField(nullable=True),
        'body': fields.IntegerField(nullable=True),
        'ca_cert_ref': fields.StringField(nullable=True),
        'oasis_cert_ref': fields.StringField(nullable=True),
        'trust_id': fields.StringField(nullable=True),
        'trustee_username': fields.StringField(nullable=True),
        'trustee_password': fields.StringField(nullable=True),
        'trustee_user_id': fields.StringField(nullable=True)
    }

    @staticmethod
    def _from_db_object(function, db_function):
        """Converts a database entity to a formal object."""
        for field in function.fields:
            if field != 'baymodel':
                function[field] = db_function[field]

        # Note(eliqiao): The following line needs to be placed outside the
        # loop because there is a dependency from baymodel to baymodel_id.
        # The baymodel_id must be populated first in the loop before it can be
        # used to find the baymodel.
        function.obj_reset_changes()
        return function

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [Function._from_db_object(cls(context), obj) for obj in db_objects]

    @base.remotable_classmethod
    def get(cls, context, function_id):
        """Find a bay based on its id or uuid and return a Bay object.

        :param function_id: the id *or* uuid of a bay.
        :param context: Security context
        :returns: a :class:`Bay` object.
        """
        if utils.is_int_like(function_id):
            return cls.get_by_id(context, function_id)
        elif utils.is_uuid_like(function_id):
            return cls.get_by_uuid(context, function_id)
        else:
            raise exception.InvalidIdentity(identity=function_id)

    @base.remotable_classmethod
    def get_by_id(cls, context, function_id):
        """Find a bay based on its integer id and return a Bay object.

        :param bay_id: the id of a bay.
        :param context: Security context
        :returns: a :class:`Bay` object.
        """
        db_bay = cls.dbapi.get_bay_by_id(context, function_id)
        bay = Function._from_db_object(cls(context), db_bay)
        return bay

    @base.remotable_classmethod
    def get_by_uuid(cls, context, uuid):
        """Find a bay based on uuid and return a :class:`Bay` object.

        :param uuid: the uuid of a bay.
        :param context: Security context
        :returns: a :class:`Bay` object.
        """
        db_bay = cls.dbapi.get_bay_by_uuid(context, uuid)
        bay = Function._from_db_object(cls(context), db_bay)
        return bay

    @base.remotable_classmethod
    def get_by_name(cls, context, name):
        """Find a bay based on name and return a Bay object.

        :param name: the logical name of a bay.
        :param context: Security context
        :returns: a :class:`Bay` object.
        """
        db_bay = cls.dbapi.get_bay_by_name(context, name)
        bay = Function._from_db_object(cls(context), db_bay)
        return bay

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None,
             sort_key=None, sort_dir=None, filters=None):
        """Return a list of Bay objects.

        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :param filters: filter dict, can includes 'baymodel_id', 'name',
                        'node_count', 'stack_id', 'api_address',
                        'node_addresses', 'project_id', 'user_id',
                        'status'(should be a status list), 'master_count'.
        :returns: a list of :class:`Bay` object.

        """
        db_functions = cls.dbapi.get_bay_list(context, limit=limit,
                                         marker=marker,
                                         sort_key=sort_key,
                                         sort_dir=sort_dir,
                                         filters=filters)
        return Function._from_db_object_list(db_functions, cls, context)

    @base.remotable
    def create(self, context=None):
        """Create a Bay record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Bay(context)

        """
        values = self.obj_get_changes()
        db_bay = self.dbapi.create_bay(values)
        self._from_db_object(self, db_bay)

    @base.remotable
    def destroy(self, context=None):
        """Delete the Bay from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Bay(context)
        """
        self.dbapi.destroy_bay(self.uuid)
        self.obj_reset_changes()

    @base.remotable
    def save(self, context=None):
        """Save updates to this Bay.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Bay(context)
        """
        updates = self.obj_get_changes()
        self.dbapi.update_bay(self.uuid, updates)

        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads updates for this Bay.

        Loads a bay with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded bay column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Bay(context)
        """
        current = self.__class__.get_by_uuid(self._context, uuid=self.uuid)
        for field in self.fields:
            if self.obj_attr_is_set(field) and self[field] != current[field]:
                self[field] = current[field]

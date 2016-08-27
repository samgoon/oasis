# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""
Base classes for storage engines
"""

import abc

from oslo_config import cfg
from oslo_db import api as db_api
import six


_BACKEND_MAPPING = {'sqlalchemy': 'oasis.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    """Return a DB API instance."""
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):
    """Base class for storage system connections."""

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

    @abc.abstractmethod
    def get_function_list(self, context, filters=None, limit=None,
                     marker=None, sort_key=None, sort_dir=None):
        """Get matching bays.

        Return a list of the specified columns for all bays that match the
        specified filters.

        :param context: The security context
        :param filters: Filters to apply. Defaults to None.

        :param limit: Maximum number of bays to return.
        :param marker: the last item of the previous page; we return the next
                       result set.
        :param sort_key: Attribute by which results should be sorted.
        :param sort_dir: direction in which results should be sorted.
                         (asc, desc)
        :returns: A list of tuples of the specified columns.
        """

    @abc.abstractmethod
    def create_function(self, values):
        """Create a new bay.

        :param values: A dict containing several items used to identify
                       and track the bay, and several dicts which are passed
                       into the Drivers when managing this bay. For example:

                       ::

                        {
                         'uuid': utils.generate_uuid(),
                         'name': 'example',
                         'type': 'virt'
                        }
        :returns: A bay.
        """

    @abc.abstractmethod
    def get_function_by_id(self, context, function_id):
        """Return a bay.

        :param context: The security context
        :param bay_id: The id of a bay.
        :returns: A bay.
        """

    @abc.abstractmethod
    def get_function_by_name(self, context, function_name):
        """Return a bay.

        :param context: The security context
        :param bay_name: The name of a bay.
        :returns: A bay.
        """

    @abc.abstractmethod
    def destroy_function(self, function_id):
        """Destroy a bay and all associated interfaces.

        :param bay_id: The id or uuid of a bay.
        """

    @abc.abstractmethod
    def update_function(self, function_id, values):
        """Update properties of a bay.

        :param bay_id: The id or uuid of a bay.
        :returns: A bay.
        :raises: BayNotFound
        """
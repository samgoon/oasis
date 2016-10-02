# All Rights Reserved.
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

from oslo_utils import timeutils
import pecan
from pecan import rest
import wsme
from wsme import types as wtypes

from oasis.api import attr_validator
from oasis.api.controllers import base
from oasis.api.controllers import link
from oasis.api.controllers.v1 import collection
from oasis.api.controllers.v1 import types
from oasis.api import expose
from oasis.api import utils as api_utils
from oasis.api.validation import validate_bay_properties
from oasis.common import exception
from oasis.common import policy
from oasis import objects
from oasis.objects import fields


class NodePoolPolicyPatchType(types.JsonPatchType):

    @staticmethod
    def internal_attrs():
        internal_attrs = ['/min_size', '/max_size', '/scaleup_adjust',
                          '/scaleup_cooldown', '/scaleup_period',
                          '/scaleup_evaluation_periods', '/scaleup_threshold',
                          '/scaledown_adjust', '/scaledown_cooldown',
                          '/scaledown_cooldown', '/scaledown_period',
                          'scaledown_evaluation_periods', 'scaledown_threshold']
        return types.JsonPatchType.internal_attrs() + internal_attrs


class NodePoolPolicy(base.APIBase):
    """API representation of a nodepool_policy.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of a nodepool_policy.
    """

    id = types.uuid

    min_size = wtypes.IntegerType(minimum=1)

    max_size = wtypes.IntegerType(minimum=1)

    scaleup_adjust = wtypes.IntegerType(minimum=1)

    scaleup_cooldown = wtypes.IntegerType(minimum=1)

    scaleup_period = wtypes.IntegerType(minimum=1)

    scaleup_evaluation_periods = wtypes.IntegerType(minimum=1)

    scaleup_threshold = wtypes.IntegerType(minimum=1)

    scaledown_adjust = wtypes.IntegerType(minimum=1)

    scaledown_cooldown = wtypes.IntegerType(minimum=1)

    scaledown_period = wtypes.IntegerType(minimum=1)

    scaledown_evaluation_periods = wtypes.IntegerType(minimum=1)

    scaledown_threshold = wtypes.IntegerType(minimum=1)

    def __init__(self, **kwargs):
        super(NodePoolPolicy, self).__init__()

        self.fields = []
        for field in objects.NodePool.fields:
            # Skip fields we do not expose.
            if not hasattr(self, field):
                continue
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @staticmethod
    def _convert_with_links(nodepool_policy, url, expand=True):
        if not expand:
            nodepool_policy.links = [link.Link.make_link('self', url,
                                         'nodepool_policies', nodepool_policy.id),
                     link.Link.make_link('bookmark', url,
                                         'nodepool_policies', nodepool_policy.id,
                                         bookmark=True)]
        return nodepool_policy

    @classmethod
    def convert_with_links(cls, rpc_nodepool_policy, expand=True):
        nodepool_policy = NodePoolPolicy(**rpc_nodepool_policy.as_dict())
        return cls._convert_with_links(nodepool_policy, pecan.request.host_url, expand)

    @classmethod
    def sample(cls, expand=True):
        sample = cls(id='27e3199e-d5bf-907e-b517-fb518e17f34c',
                     min_size=0,
                     max_size=0,
                     scaleup_adjust=0,
                     scaleup_cooldown=0,
                     scaleup_period=0,
                     scaleup_evaluation_periods=0,
                     scaleup_threshold=0,
                     scaledown_adjust=0,
                     scaledown_cooldown=0,
                     scaledown_period=0,
                     scaledown_evaluation_periods=0,
                     scaledown_threshold=0)
        return cls._convert_with_links(sample, 'http://localhost:9417', expand)


class NodePoolPolicyCollection(collection.Collection):
    """API representation of a collection of nodepool_policies."""

    nodepool_policies = [NodePoolPolicy]
    """A list containing nodepool_policies objects"""

    def __init__(self, **kwargs):
        self._type = 'nodepool_policies'

    @staticmethod
    def convert_with_links(rpc_bays, limit, url=None, expand=False, **kwargs):
        collection = NodePoolPolicyCollection()
        collection.bays = [NodePoolPolicy.convert_with_links(p, expand)
                           for p in rpc_bays]
        collection.next = collection.get_next(limit, url=url, **kwargs)
        return collection

    @classmethod
    def sample(cls):
        sample = cls()
        sample.nodepool_policies = [NodePoolPolicy.sample(expand=False)]
        return sample


class NodePoolPoliciesController(rest.RestController):
    """REST controller for NodePoolPolicies."""
    def __init__(self):
        super(NodePoolPoliciesController, self).__init__()

    _custom_actions = {
        'detail': ['GET'],
    }

    def _get_nodepool_policies_collection(self, marker, limit,
                             sort_key, sort_dir, expand=False,
                             resource_url=None):

        limit = api_utils.validate_limit(limit)
        sort_dir = api_utils.validate_sort_dir(sort_dir)

        marker_obj = None
        if marker:
            marker_obj = objects.NodePoolPolicy.get_by_uuid(pecan.request.context,
                                                 marker)

        nodepool_policies = objects.NodePoolPolicy.list(pecan.request.context, limit,
                                marker_obj, sort_key=sort_key,
                                sort_dir=sort_dir)

        return NodePoolPolicyCollection.convert_with_links(nodepool_policies, limit,
                                                url=resource_url,
                                                expand=expand,
                                                sort_key=sort_key,
                                                sort_dir=sort_dir)

    @expose.expose(NodePoolPolicyCollection, types.uuid, int, wtypes.text,
                   wtypes.text)
    def get_all(self, marker=None, limit=None, sort_key='id',
                sort_dir='asc'):
        """Retrieve a list of bays.

        :param marker: pagination marker for large data sets.
        :param limit: maximum number of resources to return in a single result.
        :param sort_key: column to sort results by. Default: id.
        :param sort_dir: direction to sort. "asc" or "desc". Default: asc.
        """
        context = pecan.request.context
        policy.enforce(context, 'nodepool_policy:get_all',
                       action='nodepool_policy:get_all')
        return self._get_nodepool_policies_collection(marker, limit, sort_key,
                                         sort_dir)

    @expose.expose(NodePoolPolicyCollection, types.uuid, int, wtypes.text,
                   wtypes.text)
    def detail(self, marker=None, limit=None, sort_key='id',
               sort_dir='asc'):
        """Retrieve a list of bays with detail.

        :param marker: pagination marker for large data sets.
        :param limit: maximum number of resources to return in a single result.
        :param sort_key: column to sort results by. Default: id.
        :param sort_dir: direction to sort. "asc" or "desc". Default: asc.
        """
        context = pecan.request.context
        policy.enforce(context, 'nodepool_policy:detail',
                       action='nodepool_policy:detail')

        # NOTE(lucasagomes): /detail should only work against collections
        parent = pecan.request.path.split('/')[:-1][-1]
        if parent != "nodepool_policies":
            raise exception.HTTPNotFound

        expand = True
        resource_url = '/'.join(['nodepool_policies', 'detail'])
        return self._get_nodepool_policies_collection(marker, limit,
                                         sort_key, sort_dir, expand,
                                         resource_url)

    @expose.expose(NodePoolPolicy, types.uuid_or_name)
    def get_one(self, nodepool_policy_ident):
        """Retrieve information about the given bay.

        :param nodepool_policy_ident: UUID of a bay or logical name of the bay.
        """
        context = pecan.request.context
        nodepool_policy = api_utils.get_resource('NodePoolPolicy', nodepool_policy_ident)
        policy.enforce(context, 'nodepool_policy:get', nodepool_policy,
                       action='nodepool_policy:get')

        return NodePoolPolicy.convert_with_links(nodepool_policy)

    @expose.expose(NodePoolPolicy, body=NodePoolPolicy, status_code=201)
    def post(self, nodepool_policy):
        """Create a new nodepool_policy.

        :param nodepool_policy: a nodepool_policy within the request body.
        """
        context = pecan.request.context
        policy.enforce(context, 'nodepool_policy:create',
                       action='nodepool_policy:create')
        nodepool_policy_dict = nodepool_policy.as_dict()
        # nodepool_policy_dict['stack_id'] = context.stack_id
        nodepool_policy_dict['project_id'] = context.project_id
        nodepool_policy_dict['user_id'] = context.user_id
        if nodepool_policy_dict.get('name') is None:
            nodepool_policy_dict['name'] = None
        if nodepool_policy_dict.get('body') is None:
            nodepool_policy_dict['body'] = None

        nodepool_policy = objects.NodePoolPolicy(context, **nodepool_policy_dict)

        nodepool_policy.create()
        # Set the HTTP Location Header
        pecan.response.location = link.build_url('nodepool_policies',
                                                 nodepool_policy.id)
        return NodePoolPolicy.convert_with_links(nodepool_policy)

        # res_nodepool_policy = pecan.request.rpcapi.nodepool_policy_create(nodepool_policy,
        #                                           nodepool_policy.nodepool_policy_create_timeout)

        # # Set the HTTP Location Header
        # pecan.response.location = link.build_url('nodepool_policies', res_nodepool_policy.uuid)
        # return NodePoolPolicy.convert_with_links(res_nodepool_policy)

    @wsme.validate(types.uuid, [NodePoolPolicyPatchType])
    @expose.expose(NodePoolPolicy, types.uuid_or_name, body=[NodePoolPolicyPatchType])
    def patch(self, nodepool_policy_ident, patch):
        """Update an existing bay.

        :param bay_ident: UUID or logical name of a bay.
        :param patch: a json PATCH document to apply to this bay.
        """
        context = pecan.request.context
        nodepool_policy = api_utils.get_resource('NodePoolPolicy', nodepool_policy_ident)
        policy.enforce(context, 'nodepool_policy:update', nodepool_policy,
                       action='nodepool_policy:update')
        try:
            nodepool_policy_dict = nodepool_policy.as_dict()
            new_nodepool_policy = NodePoolPolicy(**api_utils.apply_jsonpatch(nodepool_policy_dict, patch))
        except api_utils.JSONPATCH_EXCEPTIONS as e:
            raise exception.PatchError(patch=patch, reason=e)

        # Update only the fields that have changed
        for field in objects.NodePoolPolicy.fields:
            try:
                patch_val = getattr(new_nodepool_policy, field)
            except AttributeError:
                # Ignore fields that aren't exposed in the API
                continue
            if patch_val == wtypes.Unset:
                patch_val = None
            if nodepool_policy[field] != patch_val:
                nodepool_policy[field] = patch_val

        delta = nodepool_policy.obj_what_changed()

        validate_bay_properties(delta)

        res_nodepool_policy = pecan.request.rpcapi.bay_update(nodepool_policy)
        return NodePoolPolicy.convert_with_links(res_nodepool_policy)

    @expose.expose(None, types.uuid_or_name, status_code=204)
    def delete(self):
        """Delete a bay.

        :param bay_ident: UUID of a bay or logical name of the bay.
        """
        context = pecan.request.context
        # nodepool_policy = api_utils.get_resource('NodePoolPolicy', "dd")
        # policy.enforce(context, 'nodepool_policy:delete', nodepool_policy,
        #                action='nodepool_policy:delete')
        print 'Delete test ......'
        pecan.request.rpcapi.test()
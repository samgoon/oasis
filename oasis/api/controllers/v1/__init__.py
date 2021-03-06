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

"""
Version 1 of the Oasis API

NOTE: IN PROGRESS AND NOT FULLY IMPLEMENTED.
"""

from oslo_log import log as logging
import pecan
from pecan import rest
from webob import exc
from wsme import types as wtypes

from oasis.api.controllers import base as controllers_base
from oasis.api.controllers import link
from oasis.api.controllers.v1 import endpoint
from oasis.api.controllers.v1 import function
from oasis.api.controllers.v1 import nodepool
from oasis.api.controllers.v1 import nodepool_policy
from oasis.api.controllers.v1 import httpapi
from oasis.api.controllers.v1 import request
from oasis.api.controllers.v1 import requestheader
from oasis.api.controllers.v1 import response
from oasis.api.controllers.v1 import responsecode
from oasis.api.controllers.v1 import responsemessage
from oasis.api import expose
from oasis.i18n import _

LOG = logging.getLogger(__name__)

BASE_VERSION = 1
MIN_VER_STR = '1.0'
MAX_VER_STR = '1.0'

MIN_VER = controllers_base.Version(
    {controllers_base.Version.string: MIN_VER_STR}, MIN_VER_STR, MAX_VER_STR)
MAX_VER = controllers_base.Version(
    {controllers_base.Version.string: MAX_VER_STR},
    MIN_VER_STR, MAX_VER_STR)


class MediaType(controllers_base.APIBase):
    """A media type representation."""

    base = wtypes.text
    type = wtypes.text

    def __init__(self, base, type):
        self.base = base
        self.type = type


class V1(controllers_base.APIBase):
    """The representation of the version 1 of the API."""

    id = wtypes.text
    """The ID of the version, also acts as the release number"""

    media_types = [MediaType]
    """An array of supcontainersed media types for this version"""

    links = [link.Link]
    """Links that point to a specific URL for this version and documentation"""

    rcs = [link.Link]
    """Links to the rcs resource"""

    endpoints = [link.Link]
    """Links to the endpoints resource"""

    httpapis = [link.Link]

    responses = [link.Link]

    responsecodes = [link.Link]

    responsemessages = [link.Link]

    requests = [link.Link]

    requestheaders = [link.Link]

    functions = [link.Link]
    """Links to the functions resource"""

    nodepools = [link.Link]
    """Links to the nodepools resource"""

    nodepool_policies = [link.Link]
    """Links to the nodepool_policies resource"""

    @staticmethod
    def convert():
        v1 = V1()
        v1.id = "v1"
        v1.links = [link.Link.make_link('self', pecan.request.host_url,
                                        'v1', '', bookmark=True),
                    link.Link.make_link('describedby',
                                        'http://docs.openstack.org',
                                        'developer/oasis/dev',
                                        'api-spec-v1.html',
                                        bookmark=True, type='text/html')]
        v1.media_types = [MediaType('application/json',
                                    'application/vnd.openstack.oasis.v1+json')]
        v1.rcs = [link.Link.make_link('self', pecan.request.host_url, 'rcs', ''),
                  link.Link.make_link('bookmark', pecan.request.host_url,
                                      'rcs', '', bookmark=True)]
        v1.endpoints = [link.Link.make_link('self', pecan.request.host_url, 'endpoints', ''),
                        link.Link.make_link('bookmark', pecan.prequest.host_url, 'endpoints', '', bookmark=True)]

        v1.httpapis = [link.Link.make_link('self', pecan.request.host_url, 'httpapis', ''),
                       link.Link.make_link('bookmark', pecan.prequest.host_url, 'httpapis', '', bookmark=True)]

        v1.requests = [link.Link.make_link('self', pecan.request.host_url, 'requests', ''),
                       link.Link.make_link('bookmark', pecan.prequest.host_url, 'requests', '', bookmark=True)]

        v1.requestheaders = [link.Link.make_link('self', pecan.request.host_url, 'requestheaders', ''),
                       link.Link.make_link('bookmark', pecan.prequest.host_url, 'requestheaders', '', bookmark=True)]

        v1.responses = [link.Link.make_link('self', pecan.request.host_url, 'responses', ''),
                       link.Link.make_link('bookmark', pecan.prequest.host_url, 'responses', '', bookmark=True)]

        v1.responsecodes = [link.Link.make_link('self', pecan.request.host_url, 'responsecodes', ''),
                       link.Link.make_link('bookmark', pecan.prequest.host_url, 'responsecodes', '', bookmark=True)]

        v1.responsemessages = [link.Link.make_link('self', pecan.request.host_url, 'responsemessages', ''),
                       link.Link.make_link('bookmark', pecan.prequest.host_url, 'responsemessages', '', bookmark=True)]

        v1.functions = [link.Link.make_link('self', pecan.request.host_url, 'functions', ''),
                        link.Link.make_link('bookmark', pecan.request.host_url,
                                            'functions', '', bookmark=True)]

        v1.nodepools = [link.Link.make_link('self', pecan.request.host_url, 'nodepools', ''),
                        link.Link.make_link('bookmark', pecan.request.host_url,
                                            'nodepools', '', bookmark=True)]

        v1.nodepool_policies = [link.Link.make_link('self', pecan.request.host_url,
                                                    'nodepool_policies', ''),
                                link.Link.make_link('bookmark', pecan.request.host_url,
                                                    'nodepool_policies', '', bookmark=True)]
        return v1


class Controller(rest.RestController):
    """Version 1 API controller root."""

    endpoints = endpoint.EndpointsController()
    functions = function.FunctionsController()
    nodepools = nodepool.NodePoolsController()
    nodepool_policies = nodepool_policy.NodePoolPoliciesController()
    httpapis = httpapi.HttpApisController()
    requests = request.RequestsController()
    requestheaders = requestheader.RequestHeadersController()
    responses = response.ResponsesController()
    responsecodes = responsecode.ResponseCodesController()
    responsemessages = responsemessage.ResponseMessagesController()

    @expose.expose(V1)
    def get(self):
        # NOTE: The reason why convert() it's being called for every
        #       request is because we need to get the host url from
        #       the request object to make the links.
        return V1.convert()

    def _check_version(self, version, headers=None):
        if headers is None:
            headers = {}
        # ensure that major version in the URL matches the header
        if version.major != BASE_VERSION:
            raise exc.HTTPNotAcceptable(_(
                "Mutually exclusive versions requested. Version %(ver)s "
                "requested but not supported by this service."
                "The supported version range is: "
                "[%(min)s, %(max)s].") % {'ver': version,
                                          'min': MIN_VER_STR,
                                          'max': MAX_VER_STR},
                                        headers=headers)
        # ensure the minor version is within the supported range
        if version < MIN_VER or version > MAX_VER:
            raise exc.HTTPNotAcceptable(_(
                "Version %(ver)s was requested but the minor version is not "
                "supported by this service. The supported version range is: "
                "[%(min)s, %(max)s].") % {'ver': version, 'min': MIN_VER_STR,
                                          'max': MAX_VER_STR}, headers=headers)

    @pecan.expose()
    def _route(self, args):
        version = controllers_base.Version(
            pecan.request.headers, MIN_VER_STR, MAX_VER_STR)

        # Always set the min and max headers
        pecan.response.headers[
            controllers_base.Version.min_string] = MIN_VER_STR
        pecan.response.headers[
            controllers_base.Version.max_string] = MAX_VER_STR

        # assert that requested version is supported
        self._check_version(version, pecan.response.headers)
        pecan.response.headers[controllers_base.Version.string] = str(version)
        pecan.request.version = version
        if pecan.request.body:
            msg = ("Processing request: url: %(url)s, %(method)s, "
                   "body: %(body)s" %
                   {'url': pecan.request.url,
                    'method': pecan.request.method,
                    'body': pecan.request.body})
            LOG.debug(msg)
        else:
            msg = ("Processing request: url: %(url)s, %(method)s, " %
                   {'url': pecan.request.url,
                    'method': pecan.request.method})
            LOG.debug(msg)

        return super(Controller, self)._route(args)


__all__ = (Controller)

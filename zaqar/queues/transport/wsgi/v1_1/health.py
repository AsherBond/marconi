# Copyright (c) 2014 Rackspace, Inc.
# Copyright 2014 Catalyst IT Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from zaqar.i18n import _
from zaqar.openstack.common import log as logging
from zaqar.queues.transport import utils
from zaqar.queues.transport.wsgi import errors as wsgi_errors

LOG = logging.getLogger(__name__)


class Resource(object):

    __slots__ = ('driver',)

    def __init__(self, driver):
        self.driver = driver

    def on_get(self, req, resp, **kwargs):
        try:
            resp_dict = self.driver.health()

            resp.content_location = req.path
            resp.body = utils.to_json(resp_dict)
        except Exception as ex:
            LOG.exception(ex)
            description = _(u'Health status could not be read.')
            raise wsgi_errors.HTTPServiceUnavailable(description)
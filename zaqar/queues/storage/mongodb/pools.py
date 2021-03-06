# Copyright (c) 2013 Rackspace, Inc.
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

"""pools: an implementation of the pool management storage
controller for mongodb.

Schema:
  'n': name :: six.text_type
  'u': uri :: six.text_type
  'w': weight :: int
  'o': options :: dict
"""

import functools

from zaqar.common import utils as common_utils
from zaqar.queues.storage import base
from zaqar.queues.storage import errors
from zaqar.queues.storage.mongodb import utils

POOLS_INDEX = [
    ('n', 1)
]

# NOTE(cpp-cabrera): used for get/list operations. There's no need to
# show the marker or the _id - they're implementation details.
OMIT_FIELDS = (('_id', False),)


def _field_spec(detailed=False):
    return dict(OMIT_FIELDS + (() if detailed else (('o', False),)))


class PoolsController(base.PoolsBase):

    def __init__(self, *args, **kwargs):
        super(PoolsController, self).__init__(*args, **kwargs)

        self._col = self.driver.database.pools
        self._col.ensure_index(POOLS_INDEX,
                               background=True,
                               name='pools_name',
                               unique=True)

    @utils.raises_conn_error
    def list(self, marker=None, limit=10, detailed=False):
        query = {}
        if marker is not None:
            query['n'] = {'$gt': marker}

        cursor = self._col.find(query, fields=_field_spec(detailed),
                                limit=limit)
        normalizer = functools.partial(_normalize, detailed=detailed)
        return utils.HookedCursor(cursor, normalizer)

    @utils.raises_conn_error
    def get(self, name, detailed=False):
        res = self._col.find_one({'n': name},
                                 _field_spec(detailed))
        if not res:
            raise errors.PoolDoesNotExist(name)

        return _normalize(res, detailed)

    @utils.raises_conn_error
    def create(self, name, weight, uri, options=None):
        options = {} if options is None else options
        self._col.update({'n': name},
                         {'$set': {'n': name, 'w': weight, 'u': uri,
                                   'o': options}},
                         upsert=True)

    @utils.raises_conn_error
    def exists(self, name):
        return self._col.find_one({'n': name}) is not None

    @utils.raises_conn_error
    def update(self, name, **kwargs):
        names = ('uri', 'weight', 'options')
        fields = common_utils.fields(kwargs, names,
                                     pred=lambda x: x is not None,
                                     key_transform=lambda x: x[0])
        assert fields, '`weight`, `uri`, or `options` not found in kwargs'
        res = self._col.update({'n': name},
                               {'$set': fields},
                               upsert=False)
        if not res['updatedExisting']:
            raise errors.PoolDoesNotExist(name)

    @utils.raises_conn_error
    def delete(self, name):
        self._col.remove({'n': name}, w=0)

    @utils.raises_conn_error
    def drop_all(self):
        self._col.drop()
        self._col.ensure_index(POOLS_INDEX, unique=True)


def _normalize(pool, detailed=False):
    ret = {
        'name': pool['n'],
        'uri': pool['u'],
        'weight': pool['w'],
    }
    if detailed:
        ret['options'] = pool['o']

    return ret

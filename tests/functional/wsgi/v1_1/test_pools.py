# Copyright (c) 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import ddt

from zaqar.tests.functional import base
from zaqar.tests.functional import helpers


@ddt.ddt
class TestPools(base.V1_1FunctionalTestBase):

    server_class = base.ZaqarServer

    def setUp(self):
        super(TestPools, self).setUp()

        self.pool_url = ("{url}/{version}/pools".format(
            url=self.cfg.zaqar.url,
            version="v1.1"
        ))
        self.cfg.zaqar.version = "v1.1"

        self.skipTest("NOT IMPLEMENTED")

        self.headers = helpers.create_zaqar_headers(self.cfg)
        self.client.headers = self.headers

        self.client.set_base_url(self.pool_url)

    def tearDown(self):
        super(TestPools, self).tearDown()

    @ddt.data(
        {
            'name': "newpool",
            'weight': 10,
            'uri': "mongodb://127.0.0.1:27017"
        }
    )
    def test_insert_pool(self, params):
        """Test the registering of one pool."""
        doc = helpers.create_pool_body(
            weight=params.get('weight', 10),
            uri=params.get('uri', "mongodb://127.0.0.1:27017")
        )

        pool_name = params.get('name', "newpool")
        self.addCleanup(self.client.delete, url='/'+pool_name)

        result = self.client.put('/'+pool_name, data=doc)
        self.assertEqual(result.status_code, 201)

        # Test existence
        result = self.client.get('/'+pool_name)
        self.assertEqual(result.status_code, 200)

    @ddt.data(
        {
            'name': "newpool",
            'weight': 10,
            'uri': "mongodb://127.0.0.1:27017"
        }
    )
    def test_pool_details(self, params):
        """Get the details of a pool. Assert the respective schema."""
        doc = helpers.create_pool_body(
            weight=params.get('weight', 10),
            uri=params.get('uri', "mongodb://127.0.0.1:27017")
        )

        pool_name = params.get('name', "newpool")
        self.addCleanup(self.client.delete, url='/'+pool_name)
        result = self.client.put('/'+pool_name, data=doc)
        self.assertEqual(result.status_code, 201)

        # Test existence
        result = self.client.get('/'+pool_name+'?detailed=true')
        self.assertEqual(result.status_code, 200)
        self.assertSchema(result.json(), 'pool-detail')

    @ddt.data(
        {
            'name': "newpool",
            'weight': 10,
            'uri': "mongodb://127.0.0.1:27017"
        }
    )
    def test_delete_pool(self, params):
        """Create a pool, then delete it.

        Make sure operation is successful.
        """

        # Create the pool
        doc = helpers.create_pool_body(
            weight=params.get('weight', 10),
            uri=params.get('uri', "mongodb://127.0.0.1:27017")
        )

        pool_name = params.get('name', "newpool")
        result = self.client.put('/'+pool_name, data=doc)
        self.assertEqual(result.status_code, 201)

        # Make sure it exists
        result = self.client.get('/'+pool_name)
        self.assertEqual(result.status_code, 200)

        # Delete it
        result = self.client.delete('/'+pool_name)
        self.assertEqual(result.status_code, 204)

    @ddt.data(
        {
            'name': "newpool",
            'weight': 10,
            'uri': "mongodb://127.0.0.1:27017"
        }
    )
    def test_list_pools(self, params):
        """Add a pool. Get the list of all the pools.

        Assert respective schema
        """
        doc = helpers.create_pool_body(
            weight=params.get('weight', 10),
            uri=params.get('uri', "mongodb://127.0.0.1:27017")
        )
        pool_name = params.get('name', "newpool")
        self.addCleanup(self.client.delete, url='/'+pool_name)
        result = self.client.put('/'+pool_name, data=doc)
        self.assertEqual(result.status_code, 201)

        result = self.client.get()
        self.assertEqual(result.status_code, 200)
        self.assertSchema(result.json(), 'pool-list')

    @ddt.data(
        {
            'name': "newpool",
            'weight': 10,
            'uri': "mongodb://127.0.0.1:27017"
        }
    )
    def test_patch_pool(self, params):
        """Create a pool. Issue a patch command,

        make sure command was successful. Check details to be sure.
        """

        doc = helpers.create_pool_body(
            weight=params.get('weight', 10),
            uri=params.get('uri', "mongodb://127.0.0.1:27017")
        )
        pool_name = params.get('name', "newpool")
        self.addCleanup(self.client.delete, url='/'+pool_name)
        result = self.client.put('/'+pool_name, data=doc)
        self.assertEqual(result.status_code, 201)
        # Update that pool

        patchdoc = helpers.create_pool_body(
            weight=5,
            uri="mongodb://127.0.0.1:27017"
        )
        result = self.client.patch('/'+pool_name, data=patchdoc)
        self.assertEqual(result.status_code, 200)

        # Get the pool, check update#
        result = self.client.get('/'+pool_name)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["weight"], 5)

    @ddt.data(
        {
            'name': "newpool",
            'weight': 10,
            'uri': "mongodb://127.0.0.1:27017"
        }
    )
    def test_patch_pool_bad_data(self, params):
        """Issue a patch command without a body. Assert 400."""
        # create a pool
        doc = helpers.create_pool_body(
            weight=params.get('weight', 10),
            uri=params.get('uri', "mongodb://127.0.0.1:27017")
        )
        pool_name = params.get('name', "newpool")
        self.addCleanup(self.client.delete, url='/'+pool_name)
        result = self.client.put('/'+pool_name, data=doc)
        self.assertEqual(result.status_code, 201)

        # Update pool with bad post data. Ensure 400
        result = self.client.patch('/'+pool_name)
        self.assertEqual(result.status_code, 400)

    @ddt.data(
        {
            'name': "newpool",
            'weight': 10,
            'uri': "mongodb://127.0.0.1:27017"
        }
    )
    def test_patch_pool_non_exist(self, params):
        """Issue patch command to pool that doesn't exist. Assert 404."""
        doc = helpers.create_pool_body(
            weight=5,
            uri=params.get('uri', "mongodb://127.0.0.1:27018")
        )
        result = self.client.patch('/nonexistpool', data=doc)
        self.assertEqual(result.status_code, 404)

    @ddt.data(
        {'name': u'\u6c49\u5b57\u6f22\u5b57'},
        {'name': 'i'*65},
        {'weight': -1}
    )
    def test_insert_pool_bad_data(self, params):
        """Create pools with invalid names and weights. Assert 400."""
        doc = helpers.create_pool_body(
            weight=params.get('weight', 10),
            uri=params.get('uri', "mongodb://127.0.0.1:27017")
        )
        pool_name = params.get('name', "newpool")
        self.addCleanup(self.client.delete, url='/'+pool_name)
        result = self.client.put('/'+pool_name, data=doc)
        self.assertEqual(result.status_code, 400)

    def test_delete_pool_non_exist(self):
        """Delete a pool that doesn't exist. Assert 404."""
        result = self.client.delete('/nonexistpool')
        self.assertEqual(result.status_code, 204)

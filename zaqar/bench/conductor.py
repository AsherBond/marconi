# Copyright (c) 2014 Rackspace, Inc.
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

from __future__ import print_function

import json
import multiprocessing as mp

from zaqar.bench.config import conf
from zaqar.bench import consumer
from zaqar.bench import producer


def main():
    conf(project='zaqar', prog='zaqar-benchmark')

    downstream_queue = mp.Queue()
    procs = [mp.Process(target=worker.run, args=(downstream_queue,))
             for worker in [producer, consumer]]
    for each_proc in procs:
        each_proc.start()
    for each_proc in procs:
        each_proc.join()

    stats = {'params': {'processes': conf.processes, 'workers': conf.workers}}
    for each_proc in procs:
        stats.update(downstream_queue.get_nowait())

    if conf.verbose:
        for name, stat in stats.items():
            print(name.capitalize())
            print("\n".join("{}: {:.1f}".format(*it) for it in stat.items()))
            print('')  # Blank line
    else:
        print(json.dumps(stats))

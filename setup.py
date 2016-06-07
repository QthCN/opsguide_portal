# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
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

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT
import os
import setuptools

# In python < 2.7.4, a lazy loading of package `pbr` will break
# setuptools if some other modules registered functions in `atexit`.
# solution from: http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing  # noqa
except ImportError:
    pass


def build_protobuf():
    print('build protobuf files now.')
    protobuf_dir = './protobuf'
    protobuf_file = '{0}/ogp_msg.proto'.format(protobuf_dir)
    cmd = 'protoc -I={src_dir} --python_out=portal/protobuf {src_file}'.format(
        src_dir=protobuf_dir,
        src_file=protobuf_file
    )
    rc = os.system(cmd)
    assert rc == 0

build_protobuf()

setuptools.setup(
    setup_requires=['pbr>=1.3'],
    pbr=True)
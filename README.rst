hbase-python
^^^^^^^^^^^^

hbase-python is a python package used to work HBase.


Dependencies
------------

* Python 3.4+
* requests
* kazoo
* protobuf

Installation
------------

STEPS:

Run this command from the directory where setup.py is located:

.. code-block:: bash

    python3 setup.py bdist_wheel

Now .whl would be generated in the dist/ directory. To install it run:

.. code-block:: bash

     pip3 install dist/hbase_python-0.5-py3-none-any.whl

Configuration
------------


Tweak these values as per your needs in *hbase/conf.py*

Defaults: 

.. code-block:: bash
   
   num_threads_per_conn = 10

   num_tasks_per_conn = 500

PS: Make sure to build and install the package again after changing these values or this can edited in the installed site-packages of python directly.

Examples
--------

Get a row by key:

.. code-block:: python

    import hbase

    zk = 'sis3.ustcdm.org:2181,sis4.ustcdm.org:2181'

    if __name__ == '__main__':
        with hbase.ConnectionPool(zk).connect() as conn:
            table = conn['mytest']['videos']
            row = table.get('00001')
            print(row)
        exit()

Scan a table:

.. code-block:: python

    import hbase

    zk = 'sis3.ustcdm.org:2181,sis4.ustcdm.org:2181'

    if __name__ == '__main__':
        with hbase.ConnectionPool(zk).connect() as conn:
            table = conn['mytest']['videos']
            for row in table.scan():
                print(row)
        exit()

Put a record to a table:

.. code-block:: python

    import hbase

    zk = 'sis3.ustcdm.org:2181,sis4.ustcdm.org:2181'

    if __name__ == '__main__':
        with hbase.ConnectionPool(zk).connect() as conn:
            table = conn['mytest']['videos']
            table.put(hbase.Row(
                '0001', {
                    'cf:name': b'Lily',
                    'cf:age': b'20'
                }
            ))
        exit()

Write a file to a table:

.. code-block:: python

    import hbase

    zk = 'sis3.ustcdm.org:2181,sis4.ustcdm.org:2181'

    if __name__ == '__main__':
        with hbase.ConnectionPool(zk).connect() as conn:
            table = conn['mytest']['videos']
            table.write_file(video_file)  # default filename is "test_video.mp4"
        exit()


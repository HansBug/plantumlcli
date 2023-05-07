Installation
===================

Plantumlcli is currently hosted on PyPI. It required python >= 3.6.

You can simply install plantumlcli from PyPI with the following command:

.. code:: shell

    pip install plantumlcli

You can also install with the newest version through GitHub:

.. code:: shell

    pip install -U git+https://github.com/hansbug/plantumlcli.git@main

.. note::
    If you need to export diagrams as PDF format, please install it using

    .. code:: shell

        pip install plantumlcli[pdf]

    And make sure that your local Cairo environment is properly configured.
    See `CairoSVG's Documentation <https://cairosvg.org/documentation/>`_ for more details.


You can check your installation by the following python \
script:

.. literalinclude:: install_check.demo.py
    :language: python
    :linenos:

The output should be like below, which means your installation \
is successful.

.. literalinclude:: install_check.demo.py.txt
    :language: text
    :linenos:

Plantumlcli is still under development, you can also check out the \
documents in stable version through `https://hansbug.github.io/plantumlcli/ <https://hansbug.github.io/plantumlcli/>`_.

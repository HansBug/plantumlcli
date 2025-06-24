Quick Start
===================================

Check Environment
------------------------

We can perform a environment check using the following command:

.. literalinclude:: cli_check.demo.sh
    :language: shell
    :linenos:

In ``plantumlcli``, the available environments can be categorized into local environments and
remote environments, as follows:

* **Local Environments**: Environments based on Java (both Oracle JDK and OpenJDK are supported) and the local ``plantuml.jar`` package. UML diagram generation is achieved by invoking the ``java -jar plantuml.jar`` command.
* **Remote Environments**: Environments based on the `plantuml-server <https://github.com/plantuml/plantuml-server>`_ and the `official PlantUML website <https://www.plantuml.com/plantuml/>`_. UML images are obtained by accessing their APIs, and the images are generated remotely and loaded into the local environment.

In the current environment, we are only connected to a docker-based plantuml-server. The inspection results are as follows:

.. literalinclude:: cli_check.demo.sh.txt
    :language: text
    :linenos:


Export Diagrams From Code
----------------------------------

Here is one example plantuml code in file ``common.puml``.

.. literalinclude:: common.puml
    :language: text
    :linenos:


Export to ASCII Arts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some very simple UML diagrams can be viewed directly in the command line using ASCII art.
For example, the following code for ``helloworld.puml``:

.. literalinclude:: helloworld.puml
    :language: text
    :linenos:

Enter the following command:

.. literalinclude:: cli_text.demo.sh
    :language: shell
    :linenos:

You will see:

.. literalinclude:: cli_text.demo.sh.txt
    :language: text
    :linenos:


Export to PNG Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert the code to PNG image with the following command

.. literalinclude:: cli_png.demo.sh
    :language: shell
    :linenos:

And this is the :download:`common.dat.png <common.dat.png>`:

.. image:: common.dat.png
    :align: center


Export to SVG Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert the code to SVG image with the following command

.. literalinclude:: cli_svg.demo.sh
    :language: shell
    :linenos:

And this is the :download:`common.dat.svg <common.dat.svg>`:

.. image:: common.dat.svg
    :align: center


Export to EPS Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert the code to EPS image with the following command

.. literalinclude:: cli_eps.demo.sh
    :language: shell
    :linenos:

And this is the :download:`common.dat.eps <common.dat.eps>`.

.. warning::
    The EPS format has been deprecated and is no longer widely supported in many applications,
    so it is not recommended to continue using it. If you need to use vector graphics in LaTeX,
    it is recommended to use the PDF format. If you need to import vector graphics into Microsoft Office software,
    it is recommended to use the SVG format.

Export to PDF Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert the code to PDF image with the following command

.. literalinclude:: cli_pdf.demo.sh
    :language: shell
    :linenos:

And this is the :download:`common.dat.pdf <common.dat.pdf>`.

.. note::
    If you need to convert it to PDF format, you will need to install ``plantumlcli[pdf]`` like this:

     .. code:: shell

        pip install plantumlcli[pdf]

More Details
-------------------------

You can see the help information with

.. literalinclude:: cli_help.demo.sh
    :language: shell
    :linenos:

And this is the help information for ``plantumlcli``

.. literalinclude:: cli_help.demo.sh.txt
    :language: text
    :linenos:



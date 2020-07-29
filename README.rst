=======================
Scipion template plugin
=======================

This is a template plugin for **scipion**

==========================
Steps to adapt this plugin
==========================

IMPORTANT: To simplify the instructions all the commands would refer to an hypothetical new plugin name called "coolem".
Note that you must replace "coolem" by your plugin name.

**Clone it:**

.. code-block::

    git clone git@github.com:scipion-em/scipion-em-template.git scipion-em-coolem

**Reset the git repo**

.. code-block::

    cd scipion-em-coolem
    rm -rf .git
    git init

**Empty CHANGES.txt**

.. code-block::

    rm CHANGES.txt && touch CHANGES.txt

**Rename "myplugin" to coolem (IDE might help here)**

.. code-block::

    mv myplugin coolem

**Tidy up imports**

Tip: Search in your IDE for "myplugin" and replace by *"coolem"*

coolem/protocols.py:
 rename MyPluginPrefixHelloWorld --> CoolemPrefixHelloWorld

coolem/wizards.py:
 rename MyPluginPrefixHelloWorldWizard --> CoolemPrefixHelloWorldWizard
 Adapt imports

protcocols.conf: rename MyPluginPrefixHelloWorld --> CoolemPrefixHelloWorld


setup.py:
 update almost all values: name, description, ...

 be sure to update package data
.. code-block::

    package_data={  # Optional
       'coolem': ['icon.png', 'protocols.conf'],
    }

  and the entry point
.. code-block::

    entry_points={
        'pyworkflow.plugin': 'coolem = coolem'
    }

**Install the plugin in devel mode**

.. code-block::

    scipion3 installp -p /home/me/scipion-em-coolem --devel

TIP: If installation fails, you can access pip options like:

.. code-block::

    scipion3 python -m pip ... (list, install, uninstall)

**Customize it**
    replace icon.png with your logo.
    update the bibtex.py with your reference.

**Get rid of this content and keep the readme informative**


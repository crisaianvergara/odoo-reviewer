=========
Job Queue
=========

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:a9daec769ffd332bf2856016233b7998135670a803452704c76f4fa2d3d3fb16
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Mature-brightgreen.png
    :target: https://odoo-community.org/page/development-status
    :alt: Mature
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fqueue-lightgray.png?logo=github
    :target: https://github.com/OCA/queue/tree/13.0/queue_job
    :alt: OCA/queue
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/queue-13-0/queue-13-0-queue_job
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/queue&target_branch=13.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This addon adds an integrated Job Queue to Odoo.

It allows to postpone method calls executed asynchronously.

Jobs are executed in the background by a ``Jobrunner``, in their own transaction.

Example:

.. code-block:: python

  from odoo import models, fields, api

  class MyModel(models.Model):
     _name = 'my.model'

     def my_method(self, a, k=None):
         _logger.info('executed with a: %s and k: %s', a, k)


  class MyOtherModel(models.Model):
      _name = 'my.other.model'

      def button_do_stuff(self):
          self.env['my.model'].with_delay().my_method('a', k=2)


In the snippet of code above, when we call ``button_do_stuff``, a job **capturing
the method and arguments** will be postponed.  It will be executed as soon as the
Jobrunner has a free bucket, which can be instantaneous if no other job is
running.


Features:

* Views for jobs, jobs are stored in PostgreSQL
* Jobrunner: execute the jobs, highly efficient thanks to PostgreSQL's NOTIFY
* Channels: give a capacity for the root channel and its sub-channels and
  segregate jobs in them. Allow for instance to restrict heavy jobs to be
  executed one at a time while little ones are executed 4 at a times.
* Retries: Ability to retry jobs by raising a type of exception
* Retry Pattern: the 3 first tries, retry after 10 seconds, the 5 next tries,
  retry after 1 minutes, ...
* Job properties: priorities, estimated time of arrival (ETA), custom
  description, number of retries
* Related Actions: link an action on the job view, such as open the record
  concerned by the job

**Table of contents**

.. contents::
   :local:

Installation
============

Be sure to have the ``requests`` library.

Configuration
=============

* Using environment variables and command line:

  * Adjust environment variables (optional):

    - ``ODOO_QUEUE_JOB_CHANNELS=root:4`` or any other channels configuration.
      The default is ``root:1``

    - if ``xmlrpc_port`` is not set: ``ODOO_QUEUE_JOB_PORT=8069``

  * Start Odoo with ``--load=web,queue_job``
    and ``--workers`` greater than 1. [1]_


* Using the Odoo configuration file:

.. code-block:: ini

  [options]
  (...)
  workers = 6
  server_wide_modules = web,queue_job

  (...)
  [queue_job]
  channels = root:2

* Confirm the runner is starting correctly by checking the odoo log file:

.. code-block::

  ...INFO...queue_job.jobrunner.runner: starting
  ...INFO...queue_job.jobrunner.runner: initializing database connections
  ...INFO...queue_job.jobrunner.runner: queue job runner ready for db <dbname>
  ...INFO...queue_job.jobrunner.runner: database connections ready

* Create jobs (eg using ``base_import_async``) and observe they
  start immediately and in parallel.

* Tip: to enable debug logging for the queue job, use
  ``--log-handler=odoo.addons.queue_job:DEBUG``

.. [1] It works with the threaded Odoo server too, although this way
       of running Odoo is obviously not for production purposes.

Usage
=====

To use this module, you need to:

#. Go to ``Job Queue`` menu

Developers
~~~~~~~~~~

**Configure default options for jobs**

In earlier versions, jobs could be configured using the ``@job`` decorator.
This is now obsolete, they can be configured using optional ``queue.job.function``
and ``queue.job.channel`` XML records.

Example of channel:

.. code-block:: XML

    <record id="channel_sale" model="queue.job.channel">
        <field name="name">sale</field>
        <field name="parent_id" ref="queue_job.channel_root" />
    </record>

Example of job function:

.. code-block:: XML

    <record id="job_function_sale_order_action_done" model="queue.job.function">
        <field name="model_id" ref="sale.model_sale_order" />
        <field name="method">action_done</field>
        <field name="channel_id" ref="channel_sale" />
        <field name="related_action" eval='{"func_name": "custom_related_action"}' />
        <field name="retry_pattern" eval="{1: 60, 2: 180, 3: 10, 5: 300}" />
    </record>

The general form for the ``name`` is: ``<model.name>.method``.

The channel, related action and retry pattern options are optional, they are
documented below.

When writing modules, if 2+ modules add a job function or channel with the same
name (and parent for channels), they'll be merged in the same record, even if
they have different xmlids. On uninstall, the merged record is deleted when all
the modules using it are uninstalled.


**Job function: channel**

The channel where the job will be delayed. The default channel is ``root``.

**Job function: related action**

The *Related Action* appears as a button on the Job's view.
The button will execute the defined action.

The default one is to open the view of the record related to the job (form view
when there is a single record, list view for several records).
In many cases, the default related action is enough and doesn't need
customization, but it can be customized by providing a dictionary on the job
function:

.. code-block:: python

   {
       "enable": False,
       "func_name": "related_action_partner",
       "kwargs": {"name": "Partner"},
   }

* ``enable``: when ``False``, the button has no effect (default: ``True``)
* ``func_name``: name of the method on ``queue.job`` that returns an action
* ``kwargs``: extra arguments to pass to the related action method

Example of related action code:

.. code-block:: python

    class QueueJob(models.Model):
        _inherit = 'queue.job'

        def related_action_partner(self, name):
            self.ensure_one()
            model = self.model_name
            partner = self.records
            action = {
                'name': name,
                'type': 'ir.actions.act_window',
                'res_model': model,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': partner.id,
            }
            return action


**Job function: retry pattern**

When a job fails with a retryable error type, it is automatically
retried later. By default, the retry is always 10 minutes later.

A retry pattern can be configured on the job function. What a pattern represents
is "from X tries, postpone to Y seconds". It is expressed as a dictionary where
keys are tries and values are seconds to postpone as integers:


.. code-block:: python

   {
       1: 10,
       5: 20,
       10: 30,
       15: 300,
   }

Based on this configuration, we can tell that:

* 5 first retries are postponed 10 seconds later
* retries 5 to 10 postponed 20 seconds later
* retries 10 to 15 postponed 30 seconds later
* all subsequent retries postponed 5 minutes later

**Job Context**

The context of the recordset of the job, or any recordset passed in arguments of
a job, is transferred to the job according to an allow-list.

The default allow-list is empty for backward compatibility. The allow-list can
be customized in ``Base._job_prepare_context_before_enqueue_keys``.

Example:

.. code-block:: python

   class Base(models.AbstractModel):

       _inherit = "base"

       @api.model
       def _job_prepare_context_before_enqueue_keys(self):
           """Keys to keep in context of stored jobs

           Empty by default for backward compatibility.
           """
           return ("tz", "lang", "allowed_company_ids", "force_company", "active_test")

**Bypass jobs on running Odoo**

When you are developing (ie: connector modules) you might want
to bypass the queue job and run your code immediately.

To do so you can set `TEST_QUEUE_JOB_NO_DELAY=1` in your enviroment.

**Bypass jobs in tests**

When writing tests on job-related methods is always tricky to deal with
delayed recordsets. To make your testing life easier
you can set `test_queue_job_no_delay=True` in the context.

Tip: you can do this at test case level like this

.. code-block:: python

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(
            cls.env.context,
            test_queue_job_no_delay=True,  # no jobs thanks
        ))

Then all your tests execute the job methods synchronously
without delaying any jobs.

Known issues / Roadmap
======================

* After creating a new database or installing ``queue_job`` on an
  existing database, Odoo must be restarted for the runner to detect it.

* When Odoo shuts down normally, it waits for running jobs to finish.
  However, when the Odoo server crashes or is otherwise force-stopped,
  running jobs are interrupted while the runner has no chance to know
  they have been aborted. In such situations, jobs may remain in
  ``started`` or ``enqueued`` state after the Odoo server is halted.
  Since the runner has no way to know if they are actually running or
  not, and does not know for sure if it is safe to restart the jobs,
  it does not attempt to restart them automatically. Such stale jobs
  therefore fill the running queue and prevent other jobs to start.
  You must therefore requeue them manually, either from the Jobs view,
  or by running the following SQL statement *before starting Odoo*:

.. code-block:: sql

  update queue_job set state='pending' where state in ('started', 'enqueued')

Changelog
=========

.. [ The change log. The goal of this file is to help readers
    understand changes between version. The primary audience is
    end users and integrators. Purely technical changes such as
    code refactoring must not be mentioned here.

    This file may contain ONE level of section titles, underlined
    with the ~ (tilde) character. Other section markers are
    forbidden and will likely break the structure of the README.rst
    or other documents where this fragment is included. ]

Next
~~~~

* [ADD] Run jobrunner as a worker process instead of a thread in the main
  process (when running with --workers > 0)
* [REF] ``@job`` and ``@related_action`` deprecated, any method can be delayed,
  and configured using ``queue.job.function`` records


13.0.1.2.0 (2020-03-10)
~~~~~~~~~~~~~~~~~~~~~~~

* Fix Multi-company access rules


13.0.1.1.0 (2019-11-01)
~~~~~~~~~~~~~~~~~~~~~~~

Important: the license has been changed from AGPL3 to LGPL3.

* Remove deprecated default company method
  (details on `#180 <https://github.com/OCA/queue/pull/180>`_)


13.0.1.0.0 (2019-10-14)
~~~~~~~~~~~~~~~~~~~~~~~

* [MIGRATION] from 12.0 branched at rev. 0138cd0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/queue/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/queue/issues/new?body=module:%20queue_job%0Aversion:%2013.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Camptocamp
* ACSONE SA/NV

Contributors
~~~~~~~~~~~~

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Matthieu Dietrich <matthieu.dietrich@camptocamp.com>
* Jos De Graeve <Jos.DeGraeve@apertoso.be>
* David Lefever <dl@taktik.be>
* Laurent Mignon <laurent.mignon@acsone.eu>
* Laetitia Gangloff <laetitia.gangloff@acsone.eu>
* Cédric Pigeon <cedric.pigeon@acsone.eu>
* Tatiana Deribina <tatiana.deribina@avoin.systems>
* Souheil Bejaoui <souheil.bejaoui@acsone.eu>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

.. |maintainer-guewen| image:: https://github.com/guewen.png?size=40px
    :target: https://github.com/guewen
    :alt: guewen

Current `maintainer <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-guewen| 

This module is part of the `OCA/queue <https://github.com/OCA/queue/tree/13.0/queue_job>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.

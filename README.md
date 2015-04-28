#A/B Testing Tool
=======================

## Motivation
Harvard is a leader in both research and higher education. As Harvard changes
academic platforms, there are new opportunities to allow course staff and
education researchers access to data about how these platforms are used.
Data about learning can inform teaching to improve learning outcomes and
other success metrics. This enables a cycle of continuous, iterative improvement.

Faculty asked, and we listened. A/B testing can help identify changes in
courses that impact the success of students.

## About the tool
The A/B Testing Tool complements existing features within Canvas that provide
data about how the platform is used. An LTI optimized for Canvas, the A/B Testing Tool creates experiments that:

* divide course enrollment into sets of users that are part of a **track** unique to the course

* apply interventions by displaying different content to each track at
  **intervention points** throughout the course

For more information, take a look at [these slides](https://docs.google.com/a/g.harvard.edu/presentation/d/1Yj5ov_hfg5jryGcwVNKqIRDy12ZYmA6kkSLi24zAZRs)

----------

## In order to run locally:

Note: In order to run a command from the ab-testing-tool directory, open terminal
and go to the ab-testing tool using something like `cd ab-testing-tool`

* Run `sudo pip install -r ab_testing_tool/requirements/local.txt` from the
ab-testing-tool directory (don't use sudo if using cygwin or virtualenv).
If installing on OSX and you encountering the error `clang error: unknown argument: '-mno-fused-madd'`
when installing lxml, refer to this: http://stackoverflow.com/a/22322645/2812260

* Create an access token in Canvas (click on Settings in top right of screen,
  look for 'New Access Token' button under 'Approved Integrations' header)
  and copy this value (token needs to be a string i.e. in quotes)

* Run `cp ab_testing_tool/settings/secure.py.example ab_testing_tool/settings/secure.py`
  from the ab-testing-tool directory

* Edit the new ab_testing_tool/settings/secure.py and fill in values requested there.
  The minimum needed for local setup is as follows:
  Modify the line referring to the `course_oauth_token`,
  adding the access token from Canvas like this:
  `"course_oauth_token": "asdlkjf234aADKUEJskjdf2l3a6k7sjdf",`.

* Run `python manage.py syncdb` from the ab-testing-tool directory

* Run `python manage.py runserver` from the ab-testing-tool directory

* Install app in canvas by adding an external tool by XML.  The key and secret
  will be "test" and "secret" respectively.  Either copy the config from
  http://localhost:8000/ab-testing/lti/tool_config or use the following:

```
<?xml version="1.0" encoding="UTF-8"?>
<cartridge_basiclti_link xmlns:lticm="http://www.imsglobal.org/xsd/imslticm_v1p0"
    xmlns:blti="http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
    xmlns:lticp="http://www.imsglobal.org/xsd/imslticp_v1p0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
    xsi:schemaLocation="http://www.imsglobal.org/xsd/imslticc_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd
        http://www.imsglobal.org/xsd/imsbasiclti_v1p0
        http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0p1.xsd
        http://www.imsglobal.org/xsd/imslticm_v1p0
        http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
        http://www.imsglobal.org/xsd/imslticp_v1p0
        http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
    <blti:title>A/B Testing Tool</blti:title>
    <blti:description>Tool to allow students in a course to get different content in a module item.</blti:description>
    <blti:launch_url>http://localhost:8000/ab-testing/lti/</blti:launch_url>
    <blti:secure_launch_url>http://localhost:8000/ab-testing/lti/</blti:secure_launch_url>
    <blti:vendor/>
    <blti:extensions platform="canvas.instructure.com">
        <lticm:property name="tool_id">ab_testing_tool</lticm:property>
        <lticm:property name="privacy_level">public</lticm:property>
        <lticm:options name="resource_selection">
            <lticm:property name="url">http://localhost:8000/ab-testing/lti/resource_selection</lticm:property>
            <lticm:property name="enabled">true</lticm:property>
        </lticm:options>
        <lticm:property name="selection_width">800</lticm:property>
        <lticm:property name="selection_height">800</lticm:property>
        <lticm:options name="course_navigation">
            <lticm:property name="text">A/B Testing Tool</lticm:property>
            <lticm:property name="enabled">true</lticm:property>
            <lticm:property name="visibility">admins</lticm:property>
        </lticm:options>
    </blti:extensions>
</cartridge_basiclti_link>
```


## Updating locally:

All commands here should be run from the ab-testing-tool directory

* Update the code via `git pull`.

* Update the database with `python manage.py migrate`

* If you get an error during migrations, delete your local database and create
  a new one with `rm ab_testing_tool/db.sqlite3` and then `python manage.py migrate`.

* Run the tool via `python manage.py runserver`.

* If you get an import error, update requirements with
  `sudo pip install -r ab_testing_tool/requirements/local.txt`
  (don't use sudo if using cygwin or virtualenv).

* If a library has changed versions and secure.py needs updating, the library update
can be done via `[sudo] pip install -r ab_testing_tool/requirements/base.txt --upgrade`

## Running Tests:

* Backend (Python) tests can be ran with command: `python manage.py test`

* Frontend (Javascript) tests are written in Jasmine syntax and ran by Karma as a test runner
to interact with Phantom.js, a headless webkit, as our browser mock.
In order to be able to run these tests, you need to:
  * install Node.js and npm
  * install Node
dependencies located in `package.json` with command `sudo npm install`,
  * install Karma Command Line interface globally with command `sudo npm install -g karma-cli`,
and finally
  * if necessary, install a hidden dependency for Phantom.js with `sudo apt-get install libfontconfig` (e.g. on Ubuntu)

  You can now run frontend tests with command: `karma start karma.conf.js` (configuration file is `karma.conf.js`)

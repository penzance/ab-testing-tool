A/B Testing Tool
=======================

In order to run locally:

* copy ab_testing_tool/settings/secure.py.example to ab_teting_tool/settings/secure.py
and fill in values requested therin

* Install the appropriate requiremnts file from ab_testing_tool/requirements.
Ex. `[sudo] pip install -r ab_testing_tool/requirements/local.txt`

* clone the django_auth_lti and canvas_python_sdk libraries and install both
(via `python setup.py install`)
TODO: add these to requiremnts

* `python manage.py syncdb`

* `python manage.py runserver`

* Install app in canvas by adding an external tool by XML; the config is generated
by localhost:8000/tool_config; here is what it should generate:

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
    <blti:launch_url>http://localhost:8000/</blti:launch_url>
    <blti:secure_launch_url>http://localhost:8000/</blti:secure_launch_url>
    <blti:vendor/>
    <blti:extensions platform="canvas.instructure.com">
        <lticm:property name="tool_id">ab_testing_tool</lticm:property>
        <lticm:property name="privacy_level">public</lticm:property>
        <lticm:options name="resource_selection">
            <lticm:property name="url">http://localhost:8000/resource_selection</lticm:property>
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
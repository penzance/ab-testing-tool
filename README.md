#A/B Testing Tool
=======================

## Motivation
Harvard is a leader in both research and higher education. As Harvard changes academic platforms, there are new opportunities to allow course staff and education researchers access to data about how these platforms are used. Data about learning can inform teaching to improve learning outcomes and other success metrics. This enables a cycle of continuous, iterative improvement.

Faculty asked, and we listened. A/B testing can help identify changes in courses that impact the success of students.

## About the tool
The A/B Testing Tool complements existing features within Canvas that provide data about how the platform is used. An LTI optimized for Canvas, the A/B Testing Tool:
* divides course enrollment into sets of users that are part of a **track** unique to the course
* applies interventions by displaying different content to each track at **intervention points** throughout the course

For more information, take a look at [these slides](https://docs.google.com/a/g.harvard.edu/presentation/d/1Yj5ov_hfg5jryGcwVNKqIRDy12ZYmA6kkSLi24zAZRs)

##In order to run locally:

* Copy `ab_testing_tool/settings/secure.py.example` to create a new file `ab_testing_tool/settings/secure.py`
and fill in values requested there. If needed, create the token in Canvas (click on Settings in top right of screen, look for 'New Access Token' button under 'Approved Integrations' header) to copy over (token needs to be a string i.e. in quotes).

* Install the appropriate requiremnts file from `ab_testing_tool/requirements`.
Ex. `[sudo] pip install -r ab_testing_tool/requirements/local.txt`.

Note on installing on OSX: If encountering the error "clang error: unknown argument: '-mno-fused-madd'" when installing lxml, refer to this: http://stackoverflow.com/a/22322645/2812260

* Clone the django_auth_lti and canvas_python_sdk libraries and install both
(via `python setup.py install`)
TODO: ensure these run successfully from requirements

* Run `python manage.py syncdb` from the ab_testing_tool directory

* Run `python manage.py runserver` from the ab_testing_tool directory

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

django-project-template
=======================

Use this template to create a new Django project like this:

django-admin.py startproject _projectname_ --extension=py,pp --template=https://github.com/Harvard-University-iCommons/django-project-template/archive/master.zip

## Customizations

* Added top-level `static` and `http_static` directories.  Common assets used across multiple apps (e.g. jQuery, Bootstrap) can be stored in `static`.  For production serving, static assets from both the top-level static directory and all app-level static directories are collected into `http_static`.
* Added `settings` and `requirements` directories under the project subdirectory.  Inside those directories there are settings and requirements files for each environment: local, test, qa, production. Each of these environment-specific files inherits from a common base file.
* Sensitive data in settings (passwords, keys) are expected to be passed to the app via environment variables.  The `settings/base.py` file contains a helper method for retrieving these values from the environment.



* XML Config:
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
            <lticm:property name="url">http://localhost:8000/lti_launch</lticm:property>
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
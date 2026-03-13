@Library('libpipelines') _

hose {
    EMAIL = 'genai'
    DEVTIMEOUT = 60
    RELEASETIMEOUT = 60
    BUILDTOOL = 'make'
    BUILDTOOL_IMAGE = 'qa.int.stratio.com:10449/stratio/python-builder-3.12:1.2.3-PR15-SNAPSHOT'
    BUILDTOOL_CPU_LIMIT = '8'
    BUILDTOOL_CPU_REQUEST = '2'
    GRYPE_TEST = true
    DEPLOYONPRS = true

    DEV = { config ->
        doCompile(config)
        doUT(config)
        doPackage(config)
        doDeploy(config)
    }
}

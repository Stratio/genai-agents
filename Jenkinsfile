@Library('libpipelines') _

hose {
    EMAIL = 'genai'
    DEVTIMEOUT = 60
    RELEASETIMEOUT = 60
    BUILDTOOL = 'make'
    BUILDTOOL_IMAGE = 'stratio/python-builder-3.14:1.4.0'
    BUILDTOOL_CPU_LIMIT = '8'
    BUILDTOOL_CPU_REQUEST = '2'
    PYTHON_MODULE = true
    GRYPE_TEST = true
    LABEL_CONTROL = true
    DEPLOYONPRS = true

    DEV = { config ->
        doCompile(config)
        doUT(config)
        doPackage(config)
        doDeploy(config)

        // genai-agents-sandbox bakes this build's sandbox mandatory skills into its image
        // (sandbox-mandatory-skills-<version>.zip), so rebuild its main to pick them up.
        // doRebuildJob skips it on PR and release builds.
        stage("Rebuild genai-agents-sandbox"){
            doRebuildJob(config, 'GenAI/genai-agents-sandbox', 'main', "", false, true, false)
        }
    }
}

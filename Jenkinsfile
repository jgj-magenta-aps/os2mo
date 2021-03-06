pipeline {
  agent any

  environment {
    BROWSER = 'chromium:headless'
    VENV = "${env.WORKSPACE}/venv"
    NODE_ENV = 'testing'
    PYTEST_ADDOPTS = '--color=yes'
  }

  options {
     skipDefaultCheckout(true)
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Clean') {
      steps {
        timeout(1) {
          dir("backend") {
            sh './.jenkins/0-clean.sh'
          }

          dir("frontend") {
            sh './.jenkins/0-clean.sh'
          }
        }
      }
    }

    stage('Build') {
      steps {
        parallel(
          Backend: {
            timeout(4) {
              ansiColor('xterm') {
                dir("backend") {
                  sh './.jenkins/1-build.sh'
                }
              }
            }
          },

          Frontend: {
            timeout(4) {
              ansiColor('xterm') {
                dir("frontend") {
                  sh './.jenkins/1-build.sh'
                }
              }
            }
          }
        )
      }
    }

    stage('Checks') {
      steps {
        timeout(1) {
          ansiColor('xterm') {
            dir("backend") {
              sh './.jenkins/2-checks.sh'
            }
          }
        }
      }
    }

    stage('Tests') {
      steps {
        timeout(12) {
          ansiColor('xterm') {
            dir("backend") {
              sh './.jenkins/3-tests.sh'
            }
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        timeout(5) {
          ansiColor('xterm') {
            dir("backend") {
              sh './.jenkins/4-deploy.sh'
            }
          }
        }
      }
    }
  }

  post {
    always {
      warnings canRunOnFailed: true, consoleParsers: [
        [parserName: 'Sphinx-build'],
        [parserName: 'Pep8']
      ]

      cobertura coberturaReportFile: '*/build/coverage/*.xml',  \
        onlyStable: false,                                      \
        conditionalCoverageTargets: '90, 0, 0',                 \
        lineCoverageTargets: '95, 0, 0',                        \
        maxNumberOfBuilds: 0

      publishHTML target: [
        allowMissing: false,
        reportDir: 'docs/out/html',
        reportFiles: 'index.html',
        reportName: 'Documentation',
        reportTitles: 'Documentation',
      ]

      junit healthScaleFactor: 200.0,           \
        testResults: '*/build/reports/*.xml'

      cleanWs deleteDirs: true

    }
  }
}

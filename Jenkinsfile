pipeline {
  agent none

  environment {
    SONAR_TOKEN = credentials('Sonar-token')
    GITHUB_PAT  = credentials('github-pat')
  }

  options {
    disableConcurrentBuilds()
    timestamps()
  }

  stages {

    stage('Code Checkout') {
      agent { label 'ubuntu-1' }
      steps {
        checkout scm
        echo "Checked out branch: ${env.BRANCH_NAME}"
      }
    }


    stage('SonarQube Scan') {
      when {
        anyOf { branch 'dev'; branch 'main' }
      }
      agent { label 'ubuntu-1' }
      steps {
        withSonarQubeEnv('Sonar-Server') {
          sh '''
            echo "Running SonarQube Scan via Docker..."
            sudo docker run --rm \
              -v "$PWD:/usr/src" \
              sonarsource/sonar-scanner-cli:4.8 \
              -Dsonar.projectKey=django-chat-app \
              -Dsonar.sources=. \
              -Dsonar.host.url=http://54.234.3.115:9000 \
              -Dsonar.login=$SONAR_TOKEN
          '''
        }
      }
    }

    stage('Quality Gate') {
      when {
        anyOf { branch 'dev'; branch 'main' }
      }
      agent { label 'ubuntu-1' }
      steps {
        timeout(time: 5, unit: 'MINUTES') {
          script {
            def qg = waitForQualityGate()
            if (qg.status != 'OK') {
              error " Quality Gate failed: ${qg.status}"
            } else {
              echo " Quality Gate passed."
            }
          }
        }
      }
    }

    stage('Build') {
      agent { label 'ubuntu-2' }
      steps {
        sh '''
          echo " Setting up virtual environment..."
          python3.11 -m venv venv
          . venv/bin/activate
          pip install --upgrade pip setuptools wheel
          pip install -r requirements.txt
          echo " Build complete for branch: ${BRANCH_NAME}"
        '''
      }
    }

    stage('Run Tests') {
      when { branch 'test' }
      agent { label 'ubuntu-2' }
      steps {
        sh '''
          echo " Running tests for branch: ${BRANCH_NAME}"
          . venv/bin/activate
          python fundoo/manage.py test chat fundooapp
        '''
      }
    }

    stage('Deploy to Production') {
      when { branch 'main' }
      agent { label 'ubuntu-2' }
      steps {
        echo " Deploying production build for ${BRANCH_NAME} ..."
        sh '''
          echo "Packaging build..."
          tar czf build-${BRANCH_NAME}.tar.gz .
          echo "Transfer artifact to server..."
          echo " Deployment stage completed (placeholder)."
        '''
      }
    }
  }

  post {
    success {
      echo " Pipeline for ${BRANCH_NAME} succeeded!"
    }
    failure {
      echo " Pipeline failed for ${BRANCH_NAME}"
    }
  }
}



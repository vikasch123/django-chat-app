pipeline{
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building...'
                // Add your build commands here

            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
                // Add your test commands here
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
                sshagent (credentials: ['your-ssh-credentials-id']) {
                  
                 sh '''
                  ssh -o StrictHostKeyChecking=no user@10.0.2.5 << EOF
                
                  cd /chatapp-modified-ubuntu-22.04
                  git pull origin main
                  source venv/bin/activate
                  pip install -r requirements.txt
                  python fundoo/manage.py migrate
                  sudo systemctl restart gunicorn
                  EOF

                  '''
            }
        }
    }
}

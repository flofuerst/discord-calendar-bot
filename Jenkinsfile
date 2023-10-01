def version = '0.1.0'

podTemplate(yaml:'''
              spec:
                serviceAccountName: jenkins
                containers:
                - name: jnlp
                  image: repo.htl-md.schule:5003/jenkins/inbound-agent
                  volumeMounts:
                  - name: home-volume
                    mountPath: /home/jenkins
                  env:
                  - name: HOME
                    value: /home/jenkins
                - name: docker
                  image: repo.htl-md.schule:5003/docker:19.03.1
                  command:
                  - sleep
                  args:
                  - 99d
                  volumeMounts:
                  - name: docker-socket
                    mountPath: /var/run
                  - name: home-volume
                    mountPath: /home/jenkins
                - name: docker-daemon
                  image: repo.htl-md.schule:5003/docker:19.03.1-dind
                  securityContext:
                    privileged: true
                  volumeMounts:
                  - name: docker-socket
                    mountPath: /var/run
                volumes:
                - name: home-volume
                  emptyDir: {}
                - name: docker-socket
                  emptyDir: {}
''') {

    node(POD_LABEL) {
        stage('Pull Git Repo') {
            git url: 'git@github.com:flofuerst/discord-calendar-bot.git',
                credentialsId: 'github'
            container('docker') {
                stage ('Build and push docker image') {
                    sh label: 'Build docker image',
                       script: "docker build . -t repo.htl-md.schule:5004/pydiscordbot:latest -t repo.htl-md.schule:5004/pydiscordbot:v$version -t htlmd/pydiscordbot:v$version"
                    withCredentials([usernamePassword(credentialsId: 'nexus-deploybot', passwordVariable: 'password', usernameVariable: 'user')]) {
                          sh label: 'Login to docker repo',
                             script: 'docker login --username $user --password $password repo.htl-md.schule:5004'

                          sh label: 'Push docker image',
                             script: "docker push repo.htl-md.schule:5004/pydiscordbot:v$version"
                    }
                }
            }
        }
    }
}

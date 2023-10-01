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
                - name: buildah
                  image: quay.io/buildah/stable
                  command:
                  - sleep
                  args:
                  - 99d
                  volumeMounts:
                  - name: home-volume
                    mountPath: /home/jenkins
                volumes:
                - name: home-volume
                  emptyDir: {}
''') {

    node(POD_LABEL) {
        stage('Pull Git Repo') {
            checkout scm
            container('buildah') {
                stage ('Build and push docker image') {
                    sh label: 'Build docker image',
                       script: "buildah build . -t repo.htl-md.schule:5004/pydiscordbot:latest -t repo.htl-md.schule:5004/pydiscordbot:v$version -t htlmd/pydiscordbot:v$version"
                    withCredentials([usernamePassword(credentialsId: 'nexus-deploybot', passwordVariable: 'password', usernameVariable: 'user')]) {
                          sh label: 'Login to docker repo',
                             script: 'buildah login --username $user --password $password repo.htl-md.schule:5004'

                          sh label: 'Push docker image',
                             script: "buildah push repo.htl-md.schule:5004/pydiscordbot:v$version"
                    }
                }
            }
        }
    }
}

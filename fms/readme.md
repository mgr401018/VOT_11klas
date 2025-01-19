###File Management System

##Requirements:

-Docker & Docker-Compose
-WSL (for Windows)

##Setup:

1) Clone repo
2) Open terminal in the folder where you cloned it to
3) run `docker-compose up --build`

##App runs on localhost:5000
##Keycloak is available at localhost:8080
##MinIO is available at localhost:9003

##To get an access token execute this command:
`curl -X POST "http://localhost:8080/realms/fms_realm/protocol/openid-connect/token" -H "Content-Type: application/x-www-form-urlencoded" -d "grant_type=password" -d "client_id=fms_client" -d "username=user1" -d "password=user1" -d "email=user1@user1.com" -d "client_secret=AxA7Ai8g68RdB0gzIwamXEfoCUw4cYpL"`

(Note: replace client_secret and user details if needed (New client secret can be found in Keycloak))

#To upload files run:
`curl -X POST -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:5000/upload -F "file=@C:\Users\<user>\<path>\sample.txt"``

#To download files run:
`curl -X GET -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:5000/download/sample.txt --output sample.txt`

(Note: sample.txt can be replaced with a full download destination path)

#To update files run:
`curl -X PUT -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:5000/update/sample.txt -F "file=@sample.txt"``

#To delete files run:
`curl -X DELETE -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:5000/delete/sample.txt`

Keycloak default user and password -> admin:admin
MinIO default user and password -> minioadmin:minioadmin

# ma-challenge
This is a repositoy to upload Sebastian's solution to the challenge shared by Mi Aguila.

Challenge: I was asked to produce two microservices that could perform this functionalities:

1. Receive through an endpoint a CSV file with some coordinates, read it and store the data in a DB. 
2. Consume an external API to get additional information of the coordinates and update the data in the DB.
3. Buil 2 microservices, one ms to each activity.

Solution: 

In order to achieve the best result in the given time, I decided to make two Django services (As seen in Architecture.png),
using DRF which allow me to expose some endpoints to recieve the files and communicate microservices with each other.

Microservice 1: File Reader App, this is a service that receives the cvs file, it will receive the file, store it in the temp folder.     
Then this method will open the document within a generator to start reading row by row,  after that it will create in bulk the postcodes
elements in the DB. Finally, it will bulk_update the created elements consuming the 2 microservices which connects with the external API. To
ensure the efficiency of this task, I'm using async methods to request most post codes as possible.
For this solution I'm using the default sqlite DB that build Django, but I'll use a PostgresQL or Mongo in a production state.

Microservice 2: Post Code Consumer App, this service is the one that consumes the external API with given coordinates(args), it receive the
additional data, proccess it (it must be a 200 response from external API, otherwise, it trys one more time or until receive the data).

The Flow that I followed 'till now was to produce a branch for every big task:
1. Creation of 1st microservice.
2. Creation of the 2nd microservice.
3. Communicating the 2 microservices.
And with every commit I'm doing a pull request.

Notes:
- Both of the Apps are built with django and DRF and have the requirment.txt files to install all required tools.
- I suggest to run ms1 in 8000 port and ms2 in 7000 port, in order to communicate them and test them properly.

TODO: - To improve the efficiency of the communication and updating of the data. I also suggest to build an Apigateway to communicate this microservices.
      - I'm facing the challenge of controlling the external API number of requests, to maintain efficiency and assure every postcode has its info updated,
        i'll try to build the apigateway that allows to connect efficiently the 2 microservices.
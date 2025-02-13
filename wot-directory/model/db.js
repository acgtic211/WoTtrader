// Bring Mongoose into the project
var mongoose = require( 'mongoose' );
const dotenv = require('dotenv');
const axios = require('axios');

dotenv.config();


/*********************/
/*******MONGODB*******/
/*********************/

// Create the database connection
mongoose.connect(process.env.MONGODB_URI_DEVELOPMENT + process.env.MONGODB_DATABASE);
mongoose.set('useFindAndModify', false);

// Catch connection event
mongoose.connection.on('connected', function () {
  //console.log('Mongoose connected to ' + "mongodb://wot_admin:cosas_acg21@10.0.7.3:27017/wot-directory");
});

// Catch connection error event
mongoose.connection.on('error',function (err) {
  console.log('Mongoose connection error: ' + err);
  process.exit(1);
});

// Catch disconnection event
mongoose.connection.on('disconnected', function () {
  console.log('Mongoose disconnected');
});

// Catch end Node application event
process.on('SIGINT', function() {
  mongoose.connection.close(function () {
    console.log('Mongoose disconnected through app termination');
    process.exit(0);
  });
});


/**********************/
/********FUSEKI********/
/**********************/

checkFusekiConnection().then(result => {
  console.log(result);
}).catch(error => {
  console.error(error);
});

// Function to check Fuseki connection
async function checkFusekiConnection() {
  const fusekiEndpoint = process.env.FUSEKI_URI_DEVELOPMENT + '/sparql'; 

  try {
      // Send a simple SPARQL query to check the connection
      const response = await axios.get(fusekiEndpoint + '?query=ASK WHERE { ?s ?p ?o }');

      if (response.status === 200) {
          return { success: true, message: 'Fuseki process is online', status: 200 };
      } else {
          throw new Error('Fuseki connection failed');
      }
  } catch (error) {
      return { success: false, message: 'Fuseki connection failed', status: 500 };
  }
}




// Models
require('./thing_description');

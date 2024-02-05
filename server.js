const express = require('express');
const { MongoClient, ServerApiVersion } = require('mongodb');

const app = express();
const port = 3000;

// MongoDB connection URI
const mongoURI =
  'mongodb+srv://atlarusent:KjUMWk2FeUTiskaU@main.zwuqy9k.mongodb.net/?retryWrites=true&w=majority';

// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(mongoURI, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  },
});

// Express route to handle requests
app.get('/', async (req, res) => {
  try {
    // Connect the client to the server (optional starting in v4.7)
    await client.connect();

    // Send a ping to confirm a successful connection
    await client.db('admin').command({ ping: 1 });

    console.log('Pinged your deployment. You successfully connected to MongoDB!');

    // Now you can perform MongoDB operations using the connected client

    // For demonstration, you can fetch some data from a collection
    const collection = client.db('your_database_name').collection('your_collection_name');
    const result = await collection.find({}).toArray();
    console.log('Fetched data from MongoDB:', result);

    // Respond to the HTTP request
    res.send('Successful response. Check the console for MongoDB data.');

  } finally {
    // Ensure that the client will close when you finish/error
    await client.close();
  }
});

// Start the Express app
app.listen(port, () => {
  console.log(`Example app is listening on port ${port}.`);
});

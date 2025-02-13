db = db.getSiblingDB('node-database');
db.createCollection('thing_descriptions');
db.thing_descriptions.createIndex({ "$**": "text" },{ name: "TextIndex" })
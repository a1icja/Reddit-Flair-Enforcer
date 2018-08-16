// Config
const config = require('../config.js');

// DB
const enmap = require('enmap');
const enmapLevel = require('enmap-level');
const db = new enmap({ provider: new enmapLevel({ name: 'cooldowns' }) });

// Reddit Wrappers
const snoowrap = new (require('snoowrap'))(config['reddit']['login']);
const snoostream = require('./handlers/stream.js')(snoowrap);

// Misc. Handlers
const dbCheck = require('./handlers/dbCheck.js');

// Code
const checkInterval = setInterval(() => dbCheck(db, snoowrap), 60 * 1000);

const postStream = snoostream.submissionStream(config['reddit']['subreddit']);

postStream.on('post', (post) => {
  const id = post.id;
  const checkTime = new Date(Date.now() + 30 * 60 * 1000);

  db.set(id, { "id": id, "time": checkTime });
});
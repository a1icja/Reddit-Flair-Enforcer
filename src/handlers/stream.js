/*
  MODIFIED SNOOSTREAM (npm/snoostream)
  License avaliable at https://github.com/lobabob/snoostream/blob/master/LICENSE
*/

const Pollify = require('pollify');

function stream(options, drift = 0) {
  const snoowrap = options;
  const startTime = Math.floor(Date.now() / 1000);

  function postStream(pollFn, subreddit = 'all', opts = {}) {
    const cacheObj = { cache: [] };
    const poll = Pollify({ rate: opts.rate || 1000, mode: 'promise' }, pollFn, subreddit, opts);
    poll.on('data', data => {
      data = dedupe(data, cacheObj);
      data.filter(post => post.created_utc >= startTime - drift)
        .forEach(post => poll.emit('post', post));
    });

    return poll;
  }
  function dedupe(batch, cacheObj) {
    const diff = batch.filter(entry => cacheObj.cache.every(oldEntry => entry.id !== oldEntry.id));
    cacheObj.cache = batch;
    return diff;
  }

  return {
    commentStream(subreddit, opts) {
      const pollFn = snoowrap.getNewComments.bind(snoowrap);
      return postStream(pollFn, subreddit, opts);
    },
    submissionStream(subreddit, opts) {
      const pollFn = snoowrap.getNew.bind(snoowrap);
      return postStream(pollFn, subreddit, opts);
    }
  };
}

module.exports = stream;
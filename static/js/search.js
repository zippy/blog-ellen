var searchData = null;
var searchInput = document.getElementById('search-input');
var searchResults = document.getElementById('search-results');

if (searchInput) {
  searchInput.addEventListener('input', function(e) {
    var query = e.target.value.toLowerCase();
    if (query.length < 2) {
      searchResults.innerHTML = '';
      return;
    }
    if (!searchData) {
      loadIndex(function() {
        executeQuery(query);
      });
    } else {
      executeQuery(query);
    }
  });
}

function loadIndex(callback) {
  var url = window.location.origin + '/blog/index.json';

  fetch(url)
    .then(response => response.json())
    .then(data => {
      searchData = data;
      if (callback) callback();
    });
}

function executeQuery(query) {
  var results = searchData.filter(function(item) {
    var title = (item.title || '').toLowerCase();
    var summary = (item.summary || '').toLowerCase();
    var content = (item.content || '').toLowerCase();
    return title.includes(query) || summary.includes(query) || content.includes(query);
  });

  if (results.length > 0) {
    var html = '<ul>';
    results.slice(0, 20).forEach(function(result) {
      html += '<li><a href="' + result.permalink + '">' + result.title + '</a>';
      if (result.date) {
        html += '<span class="search-date">' + result.date + '</span>';
      }
      html += '</li>';
    });
    html += '</ul>';
    searchResults.innerHTML = html;
  } else {
    searchResults.innerHTML = '<p class="no-results">No results found</p>';
  }
}

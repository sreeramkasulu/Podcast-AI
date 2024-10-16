document.getElementById('news-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const query = document.getElementById('query').value;
    const language = document.getElementById('language').value;
    
    // Show loader
    document.getElementById('loader').style.display = 'block';
    document.getElementById('result').innerText = '';

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query, language: language })  // Send as JSON
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error); });
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('result').innerText = data.outline;
        // Handle pagination (if applicable) here
    })
    .catch(error => {
        document.getElementById('result').innerText = 'Error: ' + error.message;
    })
    .finally(() => {
        // Hide loader after fetching results
        document.getElementById('loader').style.display = 'none';
    });
});

// Example logic for pagination
let currentPage = 1;
const maxArticles = 10;

document.getElementById('prev').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        fetchArticles();
    }
});

document.getElementById('next').addEventListener('click', () => {
    currentPage++;
    fetchArticles();
});

function fetchArticles() {
    // Logic to fetch articles based on the currentPage and maxArticles
    // Update the result display and disable/enable pagination buttons accordingly
}

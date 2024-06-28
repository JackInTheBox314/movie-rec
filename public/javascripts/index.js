document.addEventListener('DOMContentLoaded', main)

async function main() {
    console.log('hello world');

    const showInfo = document.querySelector('.info-content')
    const showInfoContainer = document.querySelector('.modal-info')
    const closeInfoBtn = document.querySelector('.close-info')
    closeInfoBtn.addEventListener('click', function(){
        showInfo.replaceChildren()
        showInfoContainer.style.display = 'none';
    })

    const addShowBtn = document.querySelector('#btn-show-modal');
    const modalDiv = document.querySelector('#modal');
    const showContainer = document.querySelector('.show-container')
    const closeModalBtn = document.querySelector('.close');
    const sortSelect = document.querySelector('#sort');
    const searchFilter = document.querySelector('#search');
    const ratingSelects = document.querySelectorAll('.rating-select')

    console.log(ratingSelects)

    for (const ratingSelect of ratingSelects) {
        console.log('test')
        ratingSelect.addEventListener('change', async function(evt){
            const rating = evt.target.value;
            const title = evt.target.title;
            // console.log(showId);

            console.log('test1')

            const options = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({rating: rating, title: title})
            }

            // console.log(JSON.stringify({rating: rating, showId: showId}));

            await fetch('rating_add', options)
        })
    }


    searchFilter.addEventListener('input', function(evt){
        const input = evt.target.value.toLowerCase();
        for (const show of displayData) {
            console.log(show.title);
            const title = show.title.toLowerCase();
            console.log('Does title contain input: ' + title.includes(input))
            const showDiv = document.getElementById(show.id);
            if (!title.includes(input)){
                showDiv.style.display = 'none';
            } else {
                showDiv.style.display = 'block';
            }
        }
        console.log('success');
    })

    sortSelect.addEventListener('change', function(evt){
        const method = evt.target.value;
        if (method !== ''){
            sortBy(method);
            displayShows();
        }
    })

    closeModalBtn.addEventListener('click', function(evt){
        modalDiv.style.display = 'none';
    })

    addShowBtn.addEventListener('click', async function(evt){
        modalDiv.style.display = 'block';
    })
    
    // fetch all movies data to display
    const response = await fetch('get_all_movies')
    if (!response.ok){
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const showsData = await response.json()
    console.log(showsData)
    let displayData = JSON.parse(JSON.stringify(showsData));

    const showsDataKeys = Object.keys(showsData[0]);

    // sortBy('recentlyAdded');
    displayShows(true);

    async function displayShows(first) {
        // console.log(JSON.stringify(displayData))
        if (!first) {
            showContainer.replaceChildren();
            for (const show of displayData) {
                if (show.title.toLowerCase().includes(searchFilter.value.toLowerCase())){
                    createShowDiv(show);
                }
            }
        } else {
            for (const show of displayData) {
                createShowDiv(show);
            }
        }
    }

    function sortBy(method) {
        if (method === 'alphabetical'){
            displayData.sort((a, b) => a.title.localeCompare(b.title));
        } else if (method === 'rating'){
            displayData.sort((a, b) => a.id - (b.id));
        } else if (method === 'longest'){
            displayData.sort((a, b) => in_minutes(b.duration) - in_minutes(a.duration))
        } else if (method === 'shortest'){
            displayData.sort((a, b) => in_minutes(a.duration) - in_minutes(b.duration))
        } else if (method === 'oldest'){
            displayData.sort((a, b) => a.year - b.year)
        } else if (method === 'newest'){
            displayData.sort((a, b) => b.year - a.year)
        } else if (method === 'most_rated'){
            displayData.sort((a, b) => compute_rating(b.num_ratings) - compute_rating(a.num_ratings))
        }
    }

    function compute_rating(rating){
        if (rating.slice(-1) === 'K'){
            return rating.slice(0, -1) * 1000
        } else if (rating.slice(-1) === 'M'){
            return rating.slice(0, -1) * 1000000
        } else {
            console.log(rating)
        }
    }

    function in_minutes(time){
        let hours = 0
        let minutes = 0
        if (time.includes(' ')){
            hours = time.split(' ')[0].slice(0, -1)
            minutes = time.split(' ')[1].slice(0, -1)
        } else if (time.slice(-1) === 'h') {
            hours = time.slice(0, -1)
        } else {
            minutes = time.slice(0, -1)
        }
        return 60 * hours + minutes
    }

    function createShowDiv(show) {
        const showDiv = document.createElement('div');
        showsDataKeys.forEach((key) => {
            showDiv[key] = show[key]
        })

        showDiv.classList.add('show-box')

        const posterElement = document.createElement('img');
        posterElement.src = show.poster_url
        posterElement.title = show.title
        posterElement.onerror = "this.onerror=null; this.remove();"

        const errorElement = document.createElement('div');
        errorElement.textContent = "Already in List";
        errorElement.style.display = 'none';
        errorElement.className = 'error'

        const titleElement = document.createElement('h2');
        titleElement.textContent = show.title;

        const yearElement = document.createElement('p');
        yearElement.innerHTML = "<b>Release Year</b>: " + show.year;

        const durationElement = document.createElement('p');
        durationElement.innerHTML = '<b>Duration</b>: ' + show.duration;

        const age_ratingElement = document.createElement('p');
        age_ratingElement.innerHTML = '<b>Age Rating</b>: ' + show.age_rating;

        const star_ratingElement = document.createElement('p');
        star_ratingElement.innerHTML = '<b>User Rating</b>: ' + show.star_rating + ' (' + show.num_ratings + ')';

        const descriptionElement = document.createElement('p');
        descriptionElement.innerHTML = '<b>Description</b>: ' + show.description;

        showDiv.appendChild(posterElement)
        showDiv.appendChild(errorElement)
        showDiv.appendChild(titleElement);
        showDiv.appendChild(yearElement);
        showDiv.appendChild(durationElement);
        showDiv.appendChild(age_ratingElement);
        showDiv.appendChild(star_ratingElement);
        showDiv.appendChild(descriptionElement);


        showDiv.addEventListener('click', async function(evt) {
            console.log(evt.target)
            const title = evt.target.title;
            
            const options = {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({title: title})
            }
            // console.log(JSON.stringify({title: title}));

            const res = await fetch('show_add', options)
            const result = await res.json()

            console.log(result.error)

            if (!result.error){
                modalDiv.style.display = 'none';
                window.location.reload();
            } else {
                errorElement.style.display = 'inline';
            }
        })

        showContainer.appendChild(showDiv);

    }
}

// async function handleShowClick(movie){

//     console.log('hello')
//     console.log(movie.textContent)
//     const titleSelect = movie.textContent

//     const response = await fetch('showsData')
//     if (!response.ok){
//         throw new Error(`HTTP error! Status: ${response.status}`);
//     }
//     const showsData = await response.json()
//     console.log(showsData)

//     let curShow = null
//     for (let i = 0; i < showsData.length; i++){
//         console.log(showsData[i])
//         if (showsData[i].title == titleSelect){
//             curShow = showsData[i]
//             console.log(curShow)
//             break
//         }
//     }

//     const showInfo = document.querySelector('.info-content')
//     const showInfoContainer = document.querySelector('.modal-info')

//     const titleInfo = document.createElement('h2');
//     titleInfo.textContent = curShow.title;

//     const directorInfo = document.createElement('p');
//     directorInfo.innerHTML = "<b>Director</b>: " + curShow.director;

//     const castInfo = document.createElement('p');
//     castInfo.innerHTML = '<b>Cast</b>: ' + curShow.cast;

//     const categoryInfo = document.createElement('p');
//     categoryInfo.innerHTML = '<b>Categories</b>: ' + curShow.listed_in;

//     const dateInfo = document.createElement('p');
//     dateInfo.innerHTML = '<b>Added</b>: ' + curShow.date_added;

//     const descriptionInfo = document.createElement('p');
//     descriptionInfo.innerHTML = '<b>Description</b>: ' + curShow.description;

//     showInfo.appendChild(titleInfo);
//     showInfo.appendChild(directorInfo);
//     showInfo.appendChild(castInfo);
//     showInfo.appendChild(categoryInfo);
//     showInfo.appendChild(dateInfo);
//     showInfo.appendChild(descriptionInfo);

//     showInfoContainer.style.display='block'
// }
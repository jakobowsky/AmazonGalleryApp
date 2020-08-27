const API_URL = "http://localhost:8000/categories/";
const API_BASE_URL = "http://localhost:8000/";

window.onload = () => {
    getCategories();
}

const getCategories = () => {
    fetch(API_URL, {
        method: 'GET'
    }).then((response)=>{
        return response.json();
    }).then((data)=>{
        buildCategories(data);
    })
}

const buildCategories = (categories) => {
    let categoriesContent = "";
    for(category of categories){
        const categoryImage = category.random_photo;
        const categoryLink = `/category.html?id=${category.id}`;
        categoriesContent += `
            <a class="post-link" href="${categoryLink}">
                <div class="post">
                    <div class="post-image" style="background-image: url(${categoryImage})"></div>
                    <div class="post-content">
                        <div class="post-title">
                            <h4>${category.name}</h4>
                        </div>
                    </div>
                </div>
            </a>
        `
    }
    document.querySelector(".blog-posts").innerHTML = categoriesContent
}

var button = document.getElementById("searchButton");

button.onclick = function () {
    var text = document.getElementById('searchTerm').value;
    window.location.href = "/category.html?product=" + text;
}
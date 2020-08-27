const API_CATEGORY_URL = "http://localhost:8000/products-filter?category__id=";
const API_PRODUCTS_URL = "http://localhost:8000/products-filter?search=";
const API_BASE_URL = "http://localhost:8000/";

window.onload = () => {
  getProducts();
};

const getBackendUrl = () => {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  let productSearch = urlParams.get("product");
  if (productSearch !== null) {
    return `${API_PRODUCTS_URL}${productSearch}`;
  }
  return `${API_CATEGORY_URL}${urlParams.get("id")}`;
};

const getProducts = () => {
  fetch(getBackendUrl(), {
    method: "GET",
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      buildProducts(data);
    });
};

const buildProducts = (products) => {
  let productsContent = "";
  for (product of products) {
    const productImage = product.photo;
    productsContent += `
            <a class="post-link" href="#">
                <div class="post">
                    <div class="post-image" style="background-image: url(${productImage})"></div>
                    <div class="post-content">
                        <div class="post-title">
                            <h4>${product.title.substring(0, 30)}</h4>
                            <hr>
                            <h4>$ ${product.price}</h4>
                        </div>
                    </div>
                </div>
            </a>
        `;
  }
  document.querySelector(".blog-posts").innerHTML = productsContent;
};

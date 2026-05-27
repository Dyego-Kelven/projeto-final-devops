const api = "http://localhost:8000/products";

async function loadProducts() {
  const response = await fetch(api);
  const products = await response.json();

  const list = document.getElementById("products");
  list.innerHTML = "";

  products.forEach(product => {
    const li = document.createElement("li");

    li.innerHTML = `
      ${product.name} - R$ ${product.price}
      <button onclick="deleteProduct('${product.id}')">Excluir</button>
    `;

    list.appendChild(li);
  });
}

async function addProduct() {
  const name = document.getElementById("name").value;
  const price = document.getElementById("price").value;

  await fetch(api, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
  name: name,
  price: Number(price),
  currency: "BRL",
  stock: 10
})
  });

  loadProducts();
}

async function deleteProduct(id) {
  await fetch(`${api}/${id}`, {
    method: "DELETE"
  });

  loadProducts();
}

loadProducts();